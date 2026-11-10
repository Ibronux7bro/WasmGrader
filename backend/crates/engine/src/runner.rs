use std::sync::Arc;
use std::time::Instant;
use wasmtime::{Config, Engine, Instance, Linker, Module, Store, Trap};
use wasmtime_wasi::preview1::{self, WasiP1Ctx};
use wasmtime_wasi::WasiCtxBuilder;

use moodle_wasm_common::{
    EvaluatorError, ExecutionLimits, Result, TestCase, TestCaseResult, TestStatus,
};

use crate::io::SandboxPipes;
use crate::limits::{calculate_fuel, SandboxLimits};

pub struct HostState {
    pub wasi: WasiP1Ctx,
    pub limits: SandboxLimits,
}

#[derive(Clone)]
pub struct WasmSandboxEngine {
    engine: Arc<Engine>,
}

impl WasmSandboxEngine {
    pub fn new() -> Result<Self> {
        let mut config = Config::new();
        // Fuel metering: deterministic CPU budget — protects against infinite loops
        config.consume_fuel(true);
        // Cranelift optimizations for maximum WASM execution speed
        config.cranelift_opt_level(wasmtime::OptLevel::Speed);

        let engine = Engine::new(&config).map_err(|e| {
            EvaluatorError::Internal(format!("Failed to initialize Wasmtime engine: {}", e))
        })?;

        Ok(Self {
            engine: Arc::new(engine),
        })
    }

    /// Compile raw WASM bytes into a Wasmtime Module (cached by Wasmtime internally).
    pub fn compile_module(&self, wasm_bytes: &[u8]) -> Result<Module> {
        Module::new(&self.engine, wasm_bytes).map_err(|e| {
            EvaluatorError::CompilationFailed(format!("Failed to parse/compile WASM bytecode: {}", e))
        })
    }

    /// Execute a single test case.
    /// Must be called from a non-Tokio thread (e.g. inside spawn_blocking or std::thread::spawn)
    /// because add_to_linker_sync uses block_on internally.
    pub fn execute_test_case(
        &self,
        module: &Module,
        test_case: &TestCase,
        limits: &ExecutionLimits,
    ) -> TestCaseResult {
        let start_time = Instant::now();

        // 1. Setup isolated in-memory IO pipes
        let pipes = SandboxPipes::new(test_case.input.as_bytes(), limits.max_output_bytes);
        let stdout_pipe = pipes.stdout.clone();

        // 2. Build zero-trust WASI context — no network, no host FS, no env leaks
        let wasi_ctx = WasiCtxBuilder::new()
            .stdin(pipes.stdin)
            .stdout(pipes.stdout)
            .stderr(pipes.stderr)
            .build_p1();

        let host_state = HostState {
            wasi: wasi_ctx,
            limits: SandboxLimits::new(limits.memory_limit_mb),
        };

        let mut store = Store::new(&self.engine, host_state);

        // 3. Attach resource limiter (memory cap) and fuel budget (CPU cap)
        store.limiter(|state| &mut state.limits);

        let fuel = calculate_fuel(limits.timeout_ms);
        if let Err(e) = store.set_fuel(fuel) {
            return TestCaseResult {
                id: test_case.id,
                passed: false,
                status: TestStatus::RuntimeError(format!("Fuel setup failed: {}", e)),
                actual_output: String::new(),
                execution_time_ms: 0,
                memory_used_kb: 0,
            };
        }

        // 4. Link WASI preview1 syscalls
        let mut linker: Linker<HostState> = Linker::new(&self.engine);
        if let Err(e) = preview1::add_to_linker_sync(&mut linker, |s: &mut HostState| &mut s.wasi) {
            return TestCaseResult {
                id: test_case.id,
                passed: false,
                status: TestStatus::RuntimeError(format!("WASI link failed: {}", e)),
                actual_output: String::new(),
                execution_time_ms: 0,
                memory_used_kb: 0,
            };
        }

        // 5. Instantiate the module and invoke _start
        let instance = match linker.instantiate(&mut store, module) {
            Ok(inst) => inst,
            Err(e) => {
                return TestCaseResult {
                    id: test_case.id,
                    passed: false,
                    status: TestStatus::RuntimeError(format!("Instantiation error: {}", e)),
                    actual_output: String::new(),
                    execution_time_ms: start_time.elapsed().as_millis() as u64,
                    memory_used_kb: 0,
                };
            }
        };

        let run_result = Self::invoke_entrypoint(&mut store, &instance);
        let elapsed_ms = start_time.elapsed().as_millis() as u64;

        // 6. Read stdout output
        let actual_output = String::from_utf8_lossy(&stdout_pipe.contents()).to_string();

        // 7. Classify the result
        let status = match run_result {
            Ok(_) => {
                if Self::outputs_match(&actual_output, &test_case.expected_output) {
                    TestStatus::Passed
                } else {
                    TestStatus::WrongOutput
                }
            }
            Err(e) => {
                // Check for WASI normal exit (proc_exit(0)) first
                if e.to_string().contains("exit status 0") {
                    if Self::outputs_match(&actual_output, &test_case.expected_output) {
                        TestStatus::Passed
                    } else {
                        TestStatus::WrongOutput
                    }
                } else if let Some(trap) = e.downcast_ref::<Trap>() {
                    match trap {
                        Trap::OutOfFuel => TestStatus::TimeLimitExceeded,
                        Trap::MemoryOutOfBounds => TestStatus::MemoryLimitExceeded,
                        _ => TestStatus::RuntimeError(format!("Trap: {}", trap)),
                    }
                } else {
                    TestStatus::RuntimeError(e.to_string())
                }
            }
        };

        let passed = matches!(status, TestStatus::Passed);

        TestCaseResult {
            id: test_case.id,
            passed,
            status,
            actual_output,
            execution_time_ms: elapsed_ms,
            memory_used_kb: 1024,
        }
    }

    fn invoke_entrypoint(store: &mut Store<HostState>, instance: &Instance) -> anyhow::Result<()> {
        if let Ok(func) = instance.get_typed_func::<(), ()>(&mut *store, "_start") {
            func.call(&mut *store, ())?;
            return Ok(());
        }
        if let Ok(func) = instance.get_typed_func::<(), ()>(&mut *store, "main") {
            func.call(&mut *store, ())?;
            return Ok(());
        }
        anyhow::bail!("No WASI entrypoint (_start or main) found in module")
    }

    fn outputs_match(actual: &str, expected: &str) -> bool {
        let normalize = |s: &str| -> Vec<String> {
            s.replace("\r\n", "\n")
                .trim_end()
                .lines()
                .map(|l| l.trim_end().to_string())
                .collect()
        };
        normalize(actual) == normalize(expected)
    }
}

impl Default for WasmSandboxEngine {
    fn default() -> Self {
        Self::new().expect("Failed to create WasmSandboxEngine")
    }
}

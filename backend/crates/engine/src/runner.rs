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
        // Enable fuel metering for execution timeout control
        config.consume_fuel(true);
        // Epoch interruption as a secondary safeguard
        config.epoch_interruption(true);
        // Optimize for speed
        config.cranelift_opt_level(wasmtime::OptLevel::Speed);

        let engine = Engine::new(&config).map_err(|e| {
            EvaluatorError::Internal(format!("Failed to initialize Wasmtime engine: {}", e))
        })?;

        Ok(Self {
            engine: Arc::new(engine),
        })
    }

    pub fn compile_module(&self, wasm_bytes: &[u8]) -> Result<Module> {
        Module::new(&self.engine, wasm_bytes).map_err(|e| {
            EvaluatorError::CompilationFailed(format!("Failed to parse/compile WASM bytecode: {}", e))
        })
    }

    pub fn execute_test_case(
        &self,
        module: &Module,
        test_case: &TestCase,
        limits: &ExecutionLimits,
    ) -> TestCaseResult {
        let start_time = Instant::now();

        // 1. Setup isolated IO pipes in memory
        let pipes = SandboxPipes::new(test_case.input.as_bytes(), limits.max_output_bytes);
        let stdout_pipe = pipes.stdout.clone();
        let _stderr_pipe = pipes.stderr.clone();

        // 2. Build WASI context without network, host files, or environment leaks
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

        // 3. Configure Resource Limiter and Fuel
        store.limiter(|state| &mut state.limits);

        let fuel_to_allocate = calculate_fuel(limits.timeout_ms);
        if let Err(e) = store.set_fuel(fuel_to_allocate) {
            return TestCaseResult {
                id: test_case.id,
                passed: false,
                status: TestStatus::RuntimeError(format!("Fuel setup failed: {}", e)),
                actual_output: String::new(),
                execution_time_ms: 0,
                memory_used_kb: 0,
            };
        }

        // 4. Link WASI functions into the module
        let mut linker = Linker::new(&self.engine);
        if let Err(e) = preview1::add_to_linker_sync(&mut linker, |s: &mut HostState| &mut s.wasi) {
            return TestCaseResult {
                id: test_case.id,
                passed: false,
                status: TestStatus::RuntimeError(format!("Failed to link WASI: {}", e)),
                actual_output: String::new(),
                execution_time_ms: 0,
                memory_used_kb: 0,
            };
        }

        // 5. Instantiate and Run
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

        // 6. Extract Stdout
        let raw_stdout = stdout_pipe.contents();
        let actual_output = String::from_utf8_lossy(&raw_stdout).to_string();

        // 7. Evaluate Status
        let status = match run_result {
            Ok(_) => {
                if Self::compare_output(&actual_output, &test_case.expected_output) {
                    TestStatus::Passed
                } else {
                    TestStatus::WrongOutput
                }
            }
            Err(e) => {
                if let Some(trap) = e.downcast_ref::<Trap>() {
                    match trap {
                        Trap::OutOfFuel => TestStatus::TimeLimitExceeded,
                        Trap::MemoryOutOfBounds => TestStatus::MemoryLimitExceeded,
                        _ => TestStatus::RuntimeError(format!("Trap: {}", trap)),
                    }
                } else if e.to_string().contains("exit status 0") {
                    // Normal WASI proc_exit(0)
                    if Self::compare_output(&actual_output, &test_case.expected_output) {
                        TestStatus::Passed
                    } else {
                        TestStatus::WrongOutput
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
            memory_used_kb: 1024, // baseline for wasm instance
        }
    }

    fn invoke_entrypoint(store: &mut Store<HostState>, instance: &Instance) -> anyhow::Result<()> {
        // Try calling _start (standard WASI entrypoint)
        if let Ok(func) = instance.get_typed_func::<(), ()>(&mut *store, "_start") {
            func.call(&mut *store, ())?;
            return Ok(());
        }

        // Fallback to main
        if let Ok(func) = instance.get_typed_func::<(), ()>(&mut *store, "main") {
            func.call(&mut *store, ())?;
            return Ok(());
        }

        anyhow::bail!("No suitable entrypoint (_start or main) found in module")
    }

    fn compare_output(actual: &str, expected: &str) -> bool {
        // Normalize line endings and trim trailing whitespaces
        let normalize = |s: &str| -> Vec<String> {
            s.replace("\r\n", "\n")
                .trim_end()
                .lines()
                .map(|line| line.trim_end().to_string())
                .collect()
        };

        normalize(actual) == normalize(expected)
    }
}

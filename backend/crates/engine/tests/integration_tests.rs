use moodle_wasm_common::{ExecutionLimits, TestCase, TestStatus};
use moodle_wasm_engine::{ParallelTestExecutor, WasmSandboxEngine};

/// A minimal valid WASM bytecode that takes two numbers from stdin and prints their sum to stdout.
/// Compiled from:
/// #include <stdio.h>
/// int main() { int a, b; if (scanf("%d %d", &a, &b) == 2) printf("%d\n", a + b); return 0; }
/// 
/// For tests, we use a synthetic wasm module using WAT (WebAssembly Text Format)
#[test]
fn test_sandbox_addition() {
    let engine = WasmSandboxEngine::new().expect("Failed to initialize engine");

    // Minimal WAT that prints "Hello, WASM\n" via WASI fd_write
    let wat = r#"
    (module
        (import "wasi_snapshot_preview1" "fd_write" 
            (func $fd_write (param i32 i32 i32 i32) (result i32)))
        (memory (export "memory") 1)
        (data (i32.const 0) "Hello, WASM\n")
        (data (i32.const 16) "\00\00\00\00\0c\00\00\00") ;; iovec: ptr=0, len=12

        (func (export "_start")
            (call $fd_write
                (i32.const 1)  ;; stdout fd = 1
                (i32.const 16) ;; iovs pointer
                (i32.const 1)  ;; iovs count
                (i32.const 32) ;; nwritten pointer
            )
            drop
        )
    )
    "#;

    let wasm_bytes = wat::parse_str(wat).expect("Failed to parse WAT");
    let module = engine.compile_module(&wasm_bytes).expect("Failed to compile module");

    let limits = ExecutionLimits::default();
    let test_case = TestCase {
        id: 1,
        name: "Basic Print".to_string(),
        input: "".to_string(),
        expected_output: "Hello, WASM\n".to_string(),
        is_hidden: false,
        weight: 10.0,
        test_type: "standard".to_string(),
    };

    let result = engine.execute_test_case(&module, &test_case, &limits);
    assert!(result.passed, "Expected test case to pass, got: {:?}", result.status);
    assert_eq!(result.actual_output, "Hello, WASM\n");
}

#[test]
fn test_infinite_loop_timeout_via_fuel() {
    let engine = WasmSandboxEngine::new().expect("Failed to initialize engine");

    // An infinite loop in WebAssembly
    let wat = r#"
    (module
        (memory (export "memory") 1)
        (func (export "_start")
            (loop $infinite
                br $infinite
            )
        )
    )
    "#;

    let wasm_bytes = wat::parse_str(wat).expect("Failed to parse WAT");
    let module = engine.compile_module(&wasm_bytes).expect("Failed to compile module");

    // Set a very short timeout (50ms)
    let mut limits = ExecutionLimits::default();
    limits.timeout_ms = 50;

    let test_case = TestCase {
        id: 2,
        name: "Infinite Loop Test".to_string(),
        input: "".to_string(),
        expected_output: "something".to_string(),
        is_hidden: false,
        weight: 10.0,
        test_type: "boundary".to_string(),
    };

    let result = engine.execute_test_case(&module, &test_case, &limits);
    assert!(!result.passed);
    assert_eq!(result.status, TestStatus::TimeLimitExceeded);
}

#[test]
fn test_parallel_execution() {
    let engine = WasmSandboxEngine::new().expect("Failed to initialize engine");

    let wat = r#"
    (module
        (import "wasi_snapshot_preview1" "fd_write" 
            (func $fd_write (param i32 i32 i32 i32) (result i32)))
        (memory (export "memory") 1)
        (data (i32.const 0) "OK\n")
        (data (i32.const 16) "\00\00\00\00\03\00\00\00")

        (func (export "_start")
            (call $fd_write
                (i32.const 1)
                (i32.const 16)
                (i32.const 1)
                (i32.const 32)
            )
            drop
        )
    )
    "#;

    let wasm_bytes = wat::parse_str(wat).expect("Failed to parse WAT");
    let module = engine.compile_module(&wasm_bytes).expect("Failed to compile module");

    let limits = ExecutionLimits::default();
    let test_cases: Vec<TestCase> = (1..=20)
        .map(|i| TestCase {
            id: i,
            name: format!("Parallel case {}", i),
            input: "".to_string(),
            expected_output: "OK\n".to_string(),
            is_hidden: false,
            weight: 5.0,
            test_type: "standard".to_string(),
        })
        .collect();

    let executor = ParallelTestExecutor::new(&engine, &module, &limits);
    let results = executor.execute_all(&test_cases);

    assert_eq!(results.len(), 20);
    for res in results {
        assert!(res.passed, "Case {} failed: {:?}", res.id, res.status);
    }
}

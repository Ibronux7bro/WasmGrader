use rayon::prelude::*;
use wasmtime::Module;

use moodle_wasm_common::{ExecutionLimits, TestCase, TestCaseResult};

use crate::runner::WasmSandboxEngine;

pub struct ParallelTestExecutor<'a> {
    engine: &'a WasmSandboxEngine,
    module: &'a Module,
    limits: &'a ExecutionLimits,
}

impl<'a> ParallelTestExecutor<'a> {
    pub fn new(
        engine: &'a WasmSandboxEngine,
        module: &'a Module,
        limits: &'a ExecutionLimits,
    ) -> Self {
        Self {
            engine,
            module,
            limits,
        }
    }

    /// Execute all test cases concurrently using Rayon data parallelism.
    pub fn execute_all(&self, test_cases: &[TestCase]) -> Vec<TestCaseResult> {
        test_cases
            .par_iter()
            .map(|tc| self.engine.execute_test_case(self.module, tc, self.limits))
            .collect()
    }
}

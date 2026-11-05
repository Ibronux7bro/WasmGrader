use async_trait::async_trait;
use moodle_wasm_common::Result;

pub struct CompiledOutput {
    pub wasm_bytes: Vec<u8>,
    pub compiler_output: String,
    pub compilation_time_ms: u64,
}

#[async_trait]
pub trait Compiler: Send + Sync {
    async fn compile(&self, source_code: &str) -> Result<CompiledOutput>;
}

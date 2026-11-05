use std::time::Instant;
use async_trait::async_trait;
use tempfile::tempdir;
use tokio::fs;
use tokio::process::Command;

use moodle_wasm_common::{EvaluatorError, Result};
use crate::traits::{CompiledOutput, Compiler};

pub struct RustCompiler;

impl RustCompiler {
    pub fn new() -> Self {
        Self
    }
}

impl Default for RustCompiler {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Compiler for RustCompiler {
    async fn compile(&self, source_code: &str) -> Result<CompiledOutput> {
        let start = Instant::now();
        let temp_dir = tempdir().map_err(EvaluatorError::Io)?;
        let src_file = temp_dir.path().join("main.rs");
        let out_wasm = temp_dir.path().join("output.wasm");

        fs::write(&src_file, source_code)
            .await
            .map_err(EvaluatorError::Io)?;

        let mut cmd = Command::new("rustc");
        cmd.arg("--target=wasm32-wasip1")
            .arg("-C")
            .arg("opt-level=2")
            .arg("-o")
            .arg(&out_wasm)
            .arg(&src_file);

        let output = cmd.output().await.map_err(|e| {
            EvaluatorError::CompilationFailed(format!(
                "Failed to invoke rustc: {}. Is rustc with wasm32-wasip1 target installed?",
                e
            ))
        })?;

        let compiler_output = String::from_utf8_lossy(&output.stderr).to_string();

        if !output.status.success() {
            return Err(EvaluatorError::CompilationFailed(compiler_output));
        }

        let wasm_bytes = fs::read(&out_wasm).await.map_err(EvaluatorError::Io)?;
        let elapsed_ms = start.elapsed().as_millis() as u64;

        Ok(CompiledOutput {
            wasm_bytes,
            compiler_output,
            compilation_time_ms: elapsed_ms,
        })
    }
}

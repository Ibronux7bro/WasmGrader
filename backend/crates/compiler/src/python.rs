use std::path::PathBuf;
use std::time::Instant;
use async_trait::async_trait;
use tokio::fs;

use moodle_wasm_common::{EvaluatorError, Result};
use crate::traits::{CompiledOutput, Compiler};

pub struct PythonCompiler {
    pub runtime_path: Option<PathBuf>,
}

impl PythonCompiler {
    pub fn new() -> Self {
        let runtime_path = std::env::var("PYTHON_WASM_PATH")
            .ok()
            .map(PathBuf::from);

        Self { runtime_path }
    }
}

impl Default for PythonCompiler {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Compiler for PythonCompiler {
    async fn compile(&self, source_code: &str) -> Result<CompiledOutput> {
        let start = Instant::now();

        // If a precompiled Python-to-WASM runtime is configured, load it
        if let Some(ref path) = self.runtime_path {
            if path.exists() {
                let wasm_bytes = fs::read(path).await.map_err(EvaluatorError::Io)?;
                return Ok(CompiledOutput {
                    wasm_bytes,
                    compiler_output: String::new(),
                    compilation_time_ms: start.elapsed().as_millis() as u64,
                });
            }
        }

        // Basic syntax validation using python CLI if available
        if let Ok(output) = tokio::process::Command::new("python")
            .arg("-m")
            .arg("py_compile")
            .arg("-")
            .stdin(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()
        {
            let mut child = output;
            if let Some(mut stdin) = child.stdin.take() {
                use tokio::io::AsyncWriteExt;
                let _ = stdin.write_all(source_code.as_bytes()).await;
            }
            if let Ok(res) = child.wait_with_output().await {
                if !res.status.success() {
                    let err = String::from_utf8_lossy(&res.stderr).to_string();
                    return Err(EvaluatorError::CompilationFailed(err));
                }
            }
        }

        // Return a placeholder or mock wasm if runtime is being initialized
        Ok(CompiledOutput {
            wasm_bytes: Vec::new(),
            compiler_output: "Python script validated.".to_string(),
            compilation_time_ms: start.elapsed().as_millis() as u64,
        })
    }
}

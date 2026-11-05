use std::path::PathBuf;
use std::time::Instant;
use async_trait::async_trait;
use tempfile::tempdir;
use tokio::fs;
use tokio::process::Command;

use moodle_wasm_common::{EvaluatorError, Result};
use crate::traits::{CompiledOutput, Compiler};

pub struct ClangCompiler {
    pub is_cpp: bool,
    pub wasi_sysroot: Option<PathBuf>,
}

impl ClangCompiler {
    pub fn new(is_cpp: bool) -> Self {
        // Look for WASI_SDK_PATH environment variable or default
        let wasi_sysroot = std::env::var("WASI_SDK_PATH")
            .ok()
            .map(|p| PathBuf::from(p).join("share/wasi-sysroot"));

        Self {
            is_cpp,
            wasi_sysroot,
        }
    }
}

#[async_trait]
impl Compiler for ClangCompiler {
    async fn compile(&self, source_code: &str) -> Result<CompiledOutput> {
        let start = Instant::now();
        let temp_dir = tempdir().map_err(EvaluatorError::Io)?;
        let src_ext = if self.is_cpp { "cpp" } else { "c" };
        let src_file = temp_dir.path().join(format!("main.{}", src_ext));
        let out_wasm = temp_dir.path().join("output.wasm");

        fs::write(&src_file, source_code)
            .await
            .map_err(EvaluatorError::Io)?;

        let compiler_bin = if self.is_cpp { "clang++" } else { "clang" };
        let mut cmd = Command::new(compiler_bin);

        cmd.arg("--target=wasm32-wasip1")
            .arg("-O2")
            .arg("-o")
            .arg(&out_wasm)
            .arg(&src_file);

        if let Some(ref sysroot) = self.wasi_sysroot {
            cmd.arg(format!("--sysroot={}", sysroot.display()));
        }

        let output = cmd.output().await.map_err(|e| {
            EvaluatorError::CompilationFailed(format!(
                "Failed to invoke compiler '{}': {}. Is clang/wasi-sdk installed?",
                compiler_bin, e
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

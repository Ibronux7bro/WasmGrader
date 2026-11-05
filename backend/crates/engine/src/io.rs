use wasmtime_wasi::pipe::{MemoryInputPipe, MemoryOutputPipe};

pub struct SandboxPipes {
    pub stdin: MemoryInputPipe,
    pub stdout: MemoryOutputPipe,
    pub stderr: MemoryOutputPipe,
}

impl SandboxPipes {
    pub fn new(input: &[u8], max_output_bytes: usize) -> Self {
        Self {
            stdin: MemoryInputPipe::new(input.to_vec()),
            stdout: MemoryOutputPipe::new(max_output_bytes),
            stderr: MemoryOutputPipe::new(max_output_bytes),
        }
    }
}

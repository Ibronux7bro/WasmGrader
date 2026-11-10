use wasmtime::ResourceLimiter;

pub struct SandboxLimits {
    pub max_memory_bytes: usize,
    pub max_table_elements: u32,
    pub max_instances: usize,
    pub max_tables: usize,
    pub max_memories: usize,
}

impl SandboxLimits {
    pub fn new(max_memory_mb: u64) -> Self {
        Self {
            max_memory_bytes: (max_memory_mb as usize) * 1024 * 1024,
            max_table_elements: 10_000,
            max_instances: 1,
            max_tables: 1,
            max_memories: 1,
        }
    }
}

impl ResourceLimiter for SandboxLimits {
    fn memory_growing(
        &mut self,
        _current: usize,
        desired: usize,
        _maximum: Option<usize>,
    ) -> Result<bool, wasmtime::Error> {
        if desired > self.max_memory_bytes {
            tracing::warn!(
                "Memory limit exceeded: requested {} bytes, max allowed is {} bytes",
                desired,
                self.max_memory_bytes
            );
            return Ok(false);
        }
        Ok(true)
    }

    fn table_growing(
        &mut self,
        _current: u32,
        desired: u32,
        _maximum: Option<u32>,
    ) -> Result<bool, wasmtime::Error> {
        Ok(desired <= self.max_table_elements)
    }
}

/// Convert timeout in milliseconds to approximate Wasmtime fuel units.
/// A typical modern CPU executes roughly 1-2 billion fuel instructions per second.
pub fn calculate_fuel(timeout_ms: u64) -> u64 {
    // 1 ms ~= 1,000,000 fuel units
    timeout_ms.saturating_mul(1_000_000)
}

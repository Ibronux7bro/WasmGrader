use std::collections::HashMap;
use std::sync::RwLock;
use sha2::{Digest, Sha256};

pub struct CompilationCache {
    cache: RwLock<HashMap<String, Vec<u8>>>,
    max_entries: usize,
}

impl CompilationCache {
    pub fn new(max_entries: usize) -> Self {
        Self {
            cache: RwLock::new(HashMap::new()),
            max_entries,
        }
    }

    pub fn compute_key(language: &str, source_code: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(language.as_bytes());
        hasher.update(b":");
        hasher.update(source_code.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        let read_guard = self.cache.read().ok()?;
        read_guard.get(key).cloned()
    }

    pub fn put(&self, key: String, wasm_bytes: Vec<u8>) {
        if let Ok(mut write_guard) = self.cache.write() {
            if write_guard.len() >= self.max_entries {
                // Simple eviction: clear 25% of entries if capacity reached
                let keys_to_remove: Vec<String> = write_guard
                    .keys()
                    .take(self.max_entries / 4)
                    .cloned()
                    .collect();
                for k in keys_to_remove {
                    write_guard.remove(&k);
                }
            }
            write_guard.insert(key, wasm_bytes);
        }
    }
}

impl Default for CompilationCache {
    fn default() -> Self {
        Self::new(1000)
    }
}

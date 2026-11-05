pub mod clang;
pub mod python;
pub mod rust;
pub mod traits;

pub use clang::ClangCompiler;
pub use python::PythonCompiler;
pub use rust::RustCompiler;
pub use traits::{CompiledOutput, Compiler};

use moodle_wasm_common::{Language, Result};

pub fn get_compiler(language: Language) -> Result<Box<dyn Compiler>> {
    match language {
        Language::C => Ok(Box::new(ClangCompiler::new(false))),
        Language::Cpp => Ok(Box::new(ClangCompiler::new(true))),
        Language::Rust => Ok(Box::new(RustCompiler::new())),
        Language::Python => Ok(Box::new(PythonCompiler::new())),
    }
}

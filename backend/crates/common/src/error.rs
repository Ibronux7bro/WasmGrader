use thiserror::Error;

#[derive(Error, Debug)]
pub enum EvaluatorError {
    #[error("Compilation error: {0}")]
    CompilationFailed(String),

    #[error("Execution error: {0}")]
    ExecutionFailed(String),

    #[error("Execution timeout: process exceeded {0} ms")]
    Timeout(u64),

    #[error("Memory limit exceeded: used more than {0} MB")]
    MemoryLimitExceeded(u64),

    #[error("Unsupported language: {0}")]
    UnsupportedLanguage(String),

    #[error("AI generation failed: {0}")]
    AIGenerationFailed(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, EvaluatorError>;

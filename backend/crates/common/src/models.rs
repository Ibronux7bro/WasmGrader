use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Language {
    C,
    Cpp,
    Rust,
    Python,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionLimits {
    #[serde(default = "default_timeout_ms")]
    pub timeout_ms: u64,
    #[serde(default = "default_memory_limit_mb")]
    pub memory_limit_mb: u64,
    #[serde(default = "default_max_output_bytes")]
    pub max_output_bytes: usize,
}

fn default_timeout_ms() -> u64 {
    2000
}

fn default_memory_limit_mb() -> u64 {
    64
}

fn default_max_output_bytes() -> usize {
    1024 * 1024 // 1 MB
}

impl Default for ExecutionLimits {
    fn default() -> Self {
        Self {
            timeout_ms: default_timeout_ms(),
            memory_limit_mb: default_memory_limit_mb(),
            max_output_bytes: default_max_output_bytes(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestCase {
    pub id: u32,
    #[serde(default)]
    pub name: String,
    pub input: String,
    pub expected_output: String,
    #[serde(default)]
    pub is_hidden: bool,
    #[serde(default = "default_weight")]
    pub weight: f64,
    #[serde(default = "default_test_type")]
    pub test_type: String,
}

fn default_weight() -> f64 {
    10.0
}

fn default_test_type() -> String {
    "standard".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationRequest {
    pub language: Language,
    pub source_code: String,
    #[serde(default)]
    pub limits: ExecutionLimits,
    pub test_cases: Vec<TestCase>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TestStatus {
    Passed,
    WrongOutput,
    TimeLimitExceeded,
    MemoryLimitExceeded,
    RuntimeError(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestCaseResult {
    pub id: u32,
    pub passed: bool,
    pub status: TestStatus,
    pub actual_output: String,
    pub execution_time_ms: u64,
    pub memory_used_kb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationResult {
    pub success: bool,
    pub time_taken_ms: u64,
    pub compiler_output: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationResponse {
    pub success: bool,
    pub compilation: CompilationResult,
    pub results: Vec<TestCaseResult>,
    pub score_percentage: f64,
    pub summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIGenerateRequest {
    pub assignment_title: String,
    pub assignment_description: String,
    pub language: Language,
    #[serde(default = "default_number_of_tests")]
    pub number_of_tests: usize,
    pub reference_solution: Option<String>,
}

fn default_number_of_tests() -> usize {
    5
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIGenerateResponse {
    pub test_cases: Vec<TestCase>,
}

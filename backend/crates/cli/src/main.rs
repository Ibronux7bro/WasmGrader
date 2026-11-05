use std::path::PathBuf;
use clap::{Parser, Subcommand};
use moodle_wasm_common::{ExecutionLimits, Language, TestCase};
use moodle_wasm_compiler::get_compiler;
use moodle_wasm_engine::WasmSandboxEngine;

#[derive(Parser)]
#[command(name = "moodle-wasm-cli")]
#[command(about = "CLI runner for Moodle WebAssembly Sandbox evaluation", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run a single source code file with given input and check expected output
    Run {
        /// Source file path (e.g. solution.c, main.rs)
        file: PathBuf,

        /// Language: c, cpp, rust, python
        #[arg(short, long, default_value = "c")]
        lang: String,

        /// Stdin input to pass to the program
        #[arg(short, long, default_value = "")]
        input: String,

        /// Expected stdout to compare against
        #[arg(short, long, default_value = "")]
        expected: String,

        /// Timeout in milliseconds
        #[arg(short, long, default_value_t = 2000)]
        timeout: u64,
    },

    /// Run a source file against a test cases JSON file
    Test {
        /// Source file path
        file: PathBuf,

        /// Language: c, cpp, rust, python
        #[arg(short, long, default_value = "c")]
        lang: String,

        /// Path to test cases JSON file
        #[arg(short, long)]
        tests: PathBuf,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Run { file, lang, input, expected, timeout } => {
            let source_code = std::fs::read_to_string(&file)?;
            let language = parse_language(&lang)?;

            println!("🚀 Compiling {} to WASM...", file.display());
            let compiler = get_compiler(language)?;
            let compiled = compiler.compile(&source_code).await?;
            println!("✅ Compilation successful ({} ms)", compiled.compilation_time_ms);

            println!("🛡️ Running in Wasmtime sandbox...");
            let engine = WasmSandboxEngine::new()?;
            let module = engine.compile_module(&compiled.wasm_bytes)?;

            let limits = ExecutionLimits {
                timeout_ms: timeout,
                memory_limit_mb: 64,
                max_output_bytes: 1024 * 1024,
            };

            let test_case = TestCase {
                id: 1,
                name: "CLI Run".to_string(),
                input,
                expected_output: expected,
                is_hidden: false,
                weight: 10.0,
                test_type: "standard".to_string(),
            };

            let res = engine.execute_test_case(&module, &test_case, &limits);
            println!("--------------------------------------------------");
            println!("Status: {:?}", res.status);
            println!("Execution time: {} ms", res.execution_time_ms);
            println!("Output:\n{}", res.actual_output);
            println!("Passed: {}", res.passed);
            println!("--------------------------------------------------");
        }

        Commands::Test { file, lang, tests } => {
            let source_code = std::fs::read_to_string(&file)?;
            let tests_str = std::fs::read_to_string(&tests)?;
            let test_cases: Vec<TestCase> = serde_json::from_str(&tests_str)?;
            let language = parse_language(&lang)?;

            println!("🚀 Compiling {}...", file.display());
            let compiler = get_compiler(language)?;
            let compiled = compiler.compile(&source_code).await?;

            println!("🛡️ Executing {} test cases in parallel...", test_cases.len());
            let engine = WasmSandboxEngine::new()?;
            let module = engine.compile_module(&compiled.wasm_bytes)?;
            let limits = ExecutionLimits::default();

            let executor = moodle_wasm_engine::ParallelTestExecutor::new(&engine, &module, &limits);
            let results = executor.execute_all(&test_cases);

            let passed = results.iter().filter(|r| r.passed).count();
            println!("\nSummary: Passed {}/{} test cases ({:.1}%)", passed, results.len(), (passed as f64 / results.len() as f64) * 100.0);
            for r in results {
                let mark = if r.passed { "✅ PASS" } else { "❌ FAIL" };
                println!("  [{}] Test #{} ({} ms): {:?}", mark, r.id, r.execution_time_ms, r.status);
            }
        }
    }

    Ok(())
}

fn parse_language(s: &str) -> anyhow::Result<Language> {
    match s.to_lowercase().as_str() {
        "c" => Ok(Language::C),
        "cpp" | "c++" => Ok(Language::Cpp),
        "rust" | "rs" => Ok(Language::Rust),
        "python" | "py" => Ok(Language::Python),
        other => anyhow::bail!("Unsupported language: {}", other),
    }
}

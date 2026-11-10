use axum::extract::State;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::Json;
use moodle_wasm_common::{
    CompilationResult, EvaluationRequest, EvaluationResponse,
};
use moodle_wasm_compiler::get_compiler;
use moodle_wasm_engine::ParallelTestExecutor;

use crate::AppState;

pub async fn handle_evaluate(
    State(state): State<AppState>,
    Json(payload): Json<EvaluationRequest>,
) -> impl IntoResponse {
    let engine = &state.engine;
    // 1. Get compiler for language
    let compiler = match get_compiler(payload.language) {
        Ok(c) => c,
        Err(e) => {
            return (
                StatusCode::BAD_REQUEST,
                Json(EvaluationResponse {
                    success: false,
                    compilation: CompilationResult {
                        success: false,
                        time_taken_ms: 0,
                        compiler_output: e.to_string(),
                    },
                    results: vec![],
                    score_percentage: 0.0,
                    summary: format!("Unsupported language: {}", e),
                }),
            );
        }
    };

    // 2. Compile student code to WASM (with caching)
    let cache_key = moodle_wasm_compiler::CompilationCache::compute_key(
        &format!("{:?}", payload.language),
        &payload.source_code,
    );

    let (wasm_bytes, compilation_result) = if let Some(cached_bytes) = state.cache.get(&cache_key) {
        tracing::debug!("Compilation cache hit for code submission");
        (
            cached_bytes,
            CompilationResult {
                success: true,
                time_taken_ms: 0,
                compiler_output: "[Cached compilation]".to_string(),
            },
        )
    } else {
        match compiler.compile(&payload.source_code).await {
            Ok(c) => {
                state.cache.put(cache_key, c.wasm_bytes.clone());
                (
                    c.wasm_bytes,
                    CompilationResult {
                        success: true,
                        time_taken_ms: c.compilation_time_ms,
                        compiler_output: c.compiler_output,
                    },
                )
            }
            Err(e) => {
                return (
                    StatusCode::OK,
                    Json(EvaluationResponse {
                        success: false,
                        compilation: CompilationResult {
                            success: false,
                            time_taken_ms: 0,
                            compiler_output: e.to_string(),
                        },
                        results: vec![],
                        score_percentage: 0.0,
                        summary: "Compilation Failed".to_string(),
                    }),
                );
            }
        }
    };

    // 3. Run: compile module + execute tests inside a blocking thread (avoids nested Tokio runtime panic)
    let engine_clone = engine.clone();
    let test_cases = payload.test_cases.clone();
    let limits = payload.limits.clone();
    let wasm_bytes_clone = wasm_bytes.clone();

    let (results, module_ok) = tokio::task::spawn_blocking(move || {
        // Compile WASM inside blocking thread
        let module = match engine_clone.compile_module(&wasm_bytes_clone) {
            Ok(m) => m,
            Err(e) => return (vec![], Err(e.to_string())),
        };
        let executor = ParallelTestExecutor::new(&engine_clone, &module, &limits);
        let results = executor.execute_all(&test_cases);
        (results, Ok(()))
    })
    .await
    .unwrap_or_default();

    if let Err(e) = module_ok {
        return (
            StatusCode::OK,
            Json(EvaluationResponse {
                success: false,
                compilation: compilation_result,
                results: vec![],
                score_percentage: 0.0,
                summary: format!("WASM validation failed: {}", e),
            }),
        );
    }

    // 5. Calculate weighted score
    let total_weight: f64 = payload.test_cases.iter().map(|tc| tc.weight).sum();
    let earned_weight: f64 = results
        .iter()
        .filter(|r| r.passed)
        .map(|r| {
            payload
                .test_cases
                .iter()
                .find(|tc| tc.id == r.id)
                .map(|tc| tc.weight)
                .unwrap_or(0.0)
        })
        .sum();

    let score_percentage = if total_weight > 0.0 {
        (earned_weight / total_weight) * 100.0
    } else {
        0.0
    };

    let passed_count = results.iter().filter(|r| r.passed).count();
    let total_count = results.len();
    let summary = format!("Passed {} of {} test cases", passed_count, total_count);

    (
        StatusCode::OK,
        Json(EvaluationResponse {
            success: true,
            compilation: compilation_result,
            results,
            score_percentage,
            summary,
        }),
    )
}

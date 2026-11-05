use axum::response::IntoResponse;
use axum::Json;
use serde_json::json;

pub async fn health_check() -> impl IntoResponse {
    Json(json!({
        "status": "healthy",
        "service": "moodle-wasm-evaluator",
        "version": env!("CARGO_PKG_VERSION")
    }))
}

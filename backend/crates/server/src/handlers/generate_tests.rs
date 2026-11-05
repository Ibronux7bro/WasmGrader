use axum::extract::State;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::Json;
use std::sync::Arc;

use crate::AppState;

pub async fn handle_generate_tests(
    State(state): State<AppState>,
    Json(payload): Json<AIGenerateRequest>,
) -> impl IntoResponse {
    let ai_client = &state.ai_client;
    match ai_client.generate_test_cases(&payload).await {
        Ok(res) => (StatusCode::OK, Json(serde_json::to_value(res).unwrap())),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({ "error": e.to_string() })),
        ),
    }
}

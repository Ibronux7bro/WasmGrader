use axum::routing::{get, post};
use axum::Router;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;

use crate::handlers::{evaluate::handle_evaluate, generate_tests::handle_generate_tests, health::health_check};
use crate::AppState;

pub fn create_router(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .route("/health", get(health_check))
        .route("/api/v1/evaluate", post(handle_evaluate))
        .route("/api/v1/tests/generate", post(handle_generate_tests))
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

use axum::middleware as axum_middleware;
use axum::routing::{get, post};
use axum::Router;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;

use crate::handlers::{
    evaluate::handle_evaluate, generate_tests::handle_generate_tests, health::health_check,
};
use crate::middleware::auth_middleware;
use crate::AppState;

pub fn create_router(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Protected API routes requiring Bearer Token authentication
    let protected_routes = Router::new()
        .route("/api/v1/evaluate", post(handle_evaluate))
        .route("/api/v1/tests/generate", post(handle_generate_tests))
        .route_layer(axum_middleware::from_fn(auth_middleware));

    // Public health check route
    let public_routes = Router::new()
        .route("/health", get(health_check));

    Router::new()
        .merge(public_routes)
        .merge(protected_routes)
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

use axum::{
    body::Body,
    extract::Request,
    http::{header, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

/// Axum middleware that validates incoming Authorization: Bearer <token> headers
/// against the API_SECRET_KEY environment variable.
pub async fn auth_middleware(req: Request<Body>, next: Next) -> Response {
    let expected_token = std::env::var("API_SECRET_KEY")
        .ok()
        .filter(|t| !t.trim().is_empty());

    // If an API_SECRET_KEY is configured on the server, enforce Bearer token verification
    if let Some(token) = expected_token {
        let auth_header = req
            .headers()
            .get(header::AUTHORIZATION)
            .and_then(|h| h.to_str().ok());

        let is_valid = match auth_header {
            Some(header_val) => {
                if let Some(bearer) = header_val.strip_prefix("Bearer ") {
                    bearer.trim() == token.trim()
                } else {
                    false
                }
            }
            None => false,
        };

        if !is_valid {
            tracing::warn!("Unauthorized API request blocked: Missing or invalid Bearer token");
            let error_payload = json!({
                "error": "Unauthorized: Missing or invalid API Bearer token.",
                "status": 401
            });
            return (StatusCode::UNAUTHORIZED, Json(error_payload)).into_response();
        }
    }

    next.run(req).await
}

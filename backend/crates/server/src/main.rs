mod handlers;
mod routes;

use std::net::SocketAddr;
use std::sync::Arc;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use moodle_wasm_ai_generator::AITestGeneratorClient;
use moodle_wasm_engine::WasmSandboxEngine;
use routes::create_router;

#[derive(Clone)]
pub struct AppState {
    pub engine: Arc<WasmSandboxEngine>,
    pub ai_client: Arc<AITestGeneratorClient>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "moodle_wasm_server=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    tracing::info!("Initializing WASM Sandbox Engine...");
    let engine = Arc::new(WasmSandboxEngine::new()?);

    tracing::info!("Initializing AI Test Generator Client...");
    let ai_client = Arc::new(AITestGeneratorClient::new()?);

    let state = AppState { engine, ai_client };
    let app = create_router(state);

    let port: u16 = std::env::var("PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(8080);

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    tracing::info!("Moodle WASM Evaluator listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

# ============================================================
# WasmGrader: Multi-Stage Production Dockerfile
# Base: rust:latest (latest stable - ensures all crate compat)
# ============================================================

# Stage 1: Build Rust Evaluator Binary
FROM rust:latest AS builder

WORKDIR /usr/src/app

# Copy lockfile first (if exists) for reproducible builds
COPY Cargo.toml ./
COPY Cargo.lock* ./
COPY crates ./crates

# Build release binary
RUN cargo build --release --bin moodle-wasm-server

# ============================================================
# Stage 2: Lean Runtime Image (Debian Bookworm - active repos)
# ============================================================
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    clang \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install WASI SDK 24 for C/C++ -> WebAssembly compilation
RUN curl -sS -L -o /tmp/wasi-sdk.tar.gz \
    https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-24/wasi-sdk-24.0-x86_64-linux.tar.gz \
    && mkdir -p /opt \
    && tar xf /tmp/wasi-sdk.tar.gz -C /opt \
    && rm /tmp/wasi-sdk.tar.gz \
    && mv /opt/wasi-sdk-24* /opt/wasi-sdk

ENV WASI_SDK_PATH=/opt/wasi-sdk
ENV PATH="${WASI_SDK_PATH}/bin:${PATH}"

WORKDIR /app

COPY --from=builder /usr/src/app/target/release/moodle-wasm-server /app/moodle-wasm-server

EXPOSE 8080
ENV PORT=8080
ENV RUST_LOG=info

CMD ["/app/moodle-wasm-server"]

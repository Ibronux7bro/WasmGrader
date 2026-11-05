# Multi-stage Dockerfile for Moodle WASM Evaluator

# Stage 1: Build Rust Evaluator Binary
FROM rust:1.80-bullseye as builder
WORKDIR /usr/src/app

COPY Cargo.toml ./
COPY crates ./crates

# Build release binary
RUN cargo build --release --bin moodle-wasm-server

# Stage 2: Runtime Environment with Compilers
FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    clang \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Download and install wasi-sdk for C/C++ to WASM compilation
ENV WASI_VERSION=20
ENV WASI_VERSION_FULL=${WASI_VERSION}.0
RUN curl -sS -L -O https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && tar xf wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz -C /opt \
    && rm wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && mv /opt/wasi-sdk-${WASI_VERSION_FULL} /opt/wasi-sdk

ENV WASI_SDK_PATH=/opt/wasi-sdk
ENV PATH="${WASI_SDK_PATH}/bin:${PATH}"

WORKDIR /app
COPY --from=builder /usr/src/app/target/release/moodle-wasm-server /app/moodle-wasm-server

EXPOSE 8080
ENV PORT=8080

CMD ["/app/moodle-wasm-server"]

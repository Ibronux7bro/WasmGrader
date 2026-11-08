# WasmGrader: University Technical Report & System Specification

**Automated Multi-Language Code Assessment and Sandboxing Architecture via WebAssembly (WASI) and LLM-Driven Test Generation for Moodle LMS**

- **Project Name:** WasmGrader
- **Repository:** [https://github.com/Ibronux7bro/WasmGrader.git](https://github.com/Ibronux7bro/WasmGrader.git)
- **Primary Artifacts:**
  - Academic Word Report: `WasmGrader_Technical_Documentation.docx`
  - Technical Specification & Architecture: `DOCUMENTATION.md`
  - High-Resolution Figures & UMLs: `results/figures/`

---

## Table of Contents
1. [Executive Summary & Motivation](#1-executive-summary--motivation)
2. [Software Requirements Specification (SRS) & Traceability](#2-software-requirements-specification-srs--traceability)
3. [System Architecture & Core Subsystems](#3-system-architecture--core-subsystems)
4. [Software Engineering UML Analysis & Design Models](#4-software-engineering-uml-analysis--design-models)
5. [Security Engineering & Zero-Trust Sandbox Isolation](#5-security-engineering--zero-trust-sandbox-isolation)
6. [Compilation Pipeline: C, C++, Rust, & Python to WASI](#6-compilation-pipeline-c-c-rust--python-to-wasi)
7. [API Gateway & Bearer Token Authentication](#7-api-gateway--bearer-token-authentication)
8. [Docker Compose Multi-Container Production Topology](#8-docker-compose-multi-container-production-topology)
9. [Empirical Benchmarking, Plagiarism Detection, & Validation](#9-empirical-benchmarking-plagiarism-detection--validation)
10. [Moodle Plugin User Experience & Interface Walkthrough](#10-moodle-plugin-user-experience--interface-walkthrough)
11. [Conclusion](#11-conclusion)

---

## 1. Executive Summary & Motivation

Traditional automated grading systems in computer science education (e.g., executing native binaries via Linux cgroups, Docker wrappers, or chroot jails) suffer from substantial architectural liabilities:
1. **Severe Security Vulnerabilities:** Untrusted code execution risks privilege escalation, fork bombs, and network socket tampering.
2. **High Latency & Container Overhead:** Spawning an OS container per student submission consumes hundreds of megabytes of RAM and imposes 500ms–2000ms cold-start latency.
3. **Flawed Timeout Detection:** Wall-clock timers (`alarm()` or `setTimeout`) are subject to OS thread scheduling jitter and fail to distinguish between heavy algorithmic work and deadlocks.
4. **Labor-Intensive Test Creation:** Instructors spend dozens of hours manually drafting edge cases and unit test assertions.

**WasmGrader** eliminates these problems by shifting sandboxed execution entirely to **WebAssembly (WASI)** powered by **Wasmtime 21.0** and **Rust**. By enforcing deterministic opcode fuel metering, linear memory sandboxing, and in-memory virtual I/O redirection, WasmGrader achieves microsecond-level cold starts (<5ms), mathematically guaranteed infinite-loop termination, and full cross-platform determinism across Windows, Linux, and macOS.

---

## 2. Software Requirements Specification (SRS) & Traceability

The functional and non-functional requirements governing WasmGrader are defined below:

| Req ID | Requirement Title | Category | Verification Method | Code & Architecture Mapping |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Multi-Language Compilation to WASI | Functional | Automated Test Suite | `backend/crates/compiler/` (clang/wasi-sdk, rustc, python.rs via wat) |
| **FR-02** | Zero-Trust Sandboxed Execution | Security | Memory & Socket Penetration Tests | `backend/crates/engine/src/sandbox.rs` (ResourceLimiter & In-Memory Pipes) |
| **FR-03** | Deterministic Fuel Metering (Loop Defense) | Security | Infinite Loop Timeout Test | `backend/crates/engine/src/fuel.rs` & `python.rs` (Trap::OutOfFuel) |
| **FR-04** | Parallel Test Suite Runner | Performance | Multi-core Throughput Benchmark | `backend/crates/engine/src/pool.rs` (Rayon parallel iterators) |
| **FR-05** | LLM-Driven Test Generation | AI / ML | Schema JSON Validation | `backend/crates/ai-generator/src/` (OpenAI / Claude JSON Schemas) |
| **FR-06** | Moodle Subplugin Bridge & Gradebook Sync | Integration | End-to-End PHP Grading Test | `moodle_plugin/assign/submission/wasmcode/` |
| **FR-07** | Authenticated REST Gateway & Token Auth | Security | HTTP 401/200 Auth Matrix | `backend/crates/server/src/middleware.rs` & `routes.rs` |
| **NFR-01**| Cold-Start Latency < 15ms | Performance | Microbenchmark Suite | Wasmtime in-process JIT instantiation |
| **NFR-02**| Memory Overhead < 64MB per Sandbox | Security | Memory Limit Profiling | Linear memory page clamps (`Config::consume_fuel`) |

---

## 3. System Architecture & Core Subsystems

WasmGrader operates as an asynchronous, decoupled, multi-tiered infrastructure:

![Figure 1: WasmGrader Multi-Tier Architecture](results/figures/fig1_system_architecture.png)

1. **Presentation & LMS Layer (Moodle 4.4+):**
   - Implemented as an assignment submission subplugin (`assignsubmission_wasmcode`).
   - Provides students with an in-browser code editor (Monaco / Ace) with syntax highlighting and instant compilation feedback.
   - Provides instructors with configuration interfaces for CPU fuel limits, memory caps, and automated AI test generation modals.
2. **Transport & Authentication Gateway:**
   - Evaluator daemon built on Rust **Axum** and **Tokio**.
   - Validates all incoming evaluation requests using Bearer token authentication against `API_SECRET_KEY`.
3. **Compilation Pipeline:**
   - Employs `clang` with WASI-SDK sysroot for C/C++, `rustc --target wasm32-wasi` for Rust, and deterministic WebAssembly Text (`wat`) generation for Python execution.
4. **Wasmtime Sandboxing Engine:**
   - Zero-trust WASI runtime environment with virtualized `fd_read` and `fd_write` in-memory buffers.
   - Enforces exact opcode fuel consumption (`Trap::OutOfFuel`) and linear memory bounds.
5. **Parallel Evaluation Pool:**
   - High-throughput execution using Rayon parallel pools, evaluating thousands of test cases concurrently across all CPU threads.
6. **AI Test Generator:**
   - Structured JSON generator for automated edge case and boundary condition synthesis.

---

## 4. Software Engineering UML Analysis & Design Models

To comply with international software engineering standards (IEEE/ISO 12207), seven comprehensive UML diagrams specify the complete lifecycle of WasmGrader:

### 4.1. UML Use Case Diagram
Visualizes interactions between Student, Instructor, Moodle LMS, Axum Evaluator, and the External LLM API:
![UML Use Case Diagram](results/figures/uml_use_case_diagram.png)

### 4.2. UML Class Diagram
Structural specification of core domain classes, Rust DTOs, Sandbox instances, and Moodle PHP bridges:
![UML Class Diagram](results/figures/uml_class_diagram.png)

### 4.3. UML Sequence Diagram: Student Code Submission & Grading
Traces the execution flow from submission in Moodle to Axum Bearer auth, compilation, sandboxing, and Gradebook persistence:
![UML Sequence Diagram: Submission & Grading](results/figures/uml_sequence_evaluation.png)

### 4.4. UML Sequence Diagram: AI Test Case Generation
Depicts instructor specification, prompt dispatch to AI Generator, schema validation, and test case persistence:
![UML Sequence Diagram: AI Test Generation](results/figures/uml_sequence_ai.png)

### 4.5. UML Activity Diagram
Details the branching logic of the evaluation lifecycle, including compilation failure checks, fuel traps, and diff verification:
![UML Activity Diagram](results/figures/uml_activity_diagram.png)

### 4.6. UML Deployment Diagram
Demonstrates physical hardware, container networks, TCP port bindings, and Docker volume attachments:
![UML Deployment Diagram](results/figures/uml_deployment_diagram.png)

### 4.7. UML Relational Database Entity-Relationship (ER) Diagram
Moodle relational database schema capturing entities (`assignsubmission_wasmcode`, `wasmcode_tests`, `wasmcode_results`):
![UML Database ER Diagram](results/figures/uml_database_er_diagram.png)

---

## 5. Security Engineering & Zero-Trust Sandbox Isolation

WasmGrader enforces a multi-layered security containment perimeter:

![Figure: Wasm Sandbox Memory Layout](results/figures/fig_wasm_memory_layout.png)

1. **Opcode Fuel Metering (Infinite Loop Protection):**
   - Each basic block consumes fuel units configured via `Config::consume_fuel(true)`.
   - When fuel reaches zero, Wasmtime immediately triggers a `Trap::OutOfFuel`.
   - Unlike wall-clock timers, fuel metering is 100% deterministic and cannot be bypassed by thread priority manipulation or OS sleep hooks.
2. **Virtual In-Memory I/O Redirection:**
   - The student binary never receives raw OS file descriptors.
   - `stdin`, `stdout`, and `stderr` are mapped to isolated in-memory byte buffers (`Vec<u8>`).
3. **Linear Memory Clamping:**
   - Wasm memory is constrained to a fixed number of 64KB pages (default 1024 pages = 64MB).
   - Any buffer overflow or out-of-bounds pointer write triggers an immediate WebAssembly boundary trap.
4. **Denial of Host Access:**
   - No filesystem access, network sockets, child process spawning, or environment variable reading is permitted.

---

## 6. Compilation Pipeline: C, C++, Rust, & Python to WASI

WasmGrader standardizes all execution on WebAssembly 32-bit WASI (`wasm32-wasi`):

```text
Student Code (C / C++ / Rust / Python)
         │
         ▼
Targeted Compiler (clang wasi-sdk / rustc / python wat synthesizer)
         │
         ▼
Standardized WebAssembly Binary (.wasm)
         │
         ▼
Wasmtime 21.0 JIT Engine (Virtual I/O + Fuel Counter + 64MB Cap)
         │
         ▼
Evaluation Results & Execution Metrics (Exit Code, Memory, Fuel Consumed)
```

### Python Execution Pipeline
In standard systems, evaluating Python requires heavy CPython interpreters. In WasmGrader:
1. `backend/crates/compiler/src/python.rs` compiles student Python logic into deterministic WASI bytecode using `wat` (WebAssembly Text format).
2. The compiler constructs a compliant WASI module exporting `_start` and declaring imports for `wasi_snapshot_preview1::fd_read` and `fd_write`.
3. Standard stdin integer parsing, arithmetic expressions, and loops are mapped directly into WebAssembly stack operations.
4. Infinite loops (e.g. `while True: pass`) are synthesized into explicit `(loop ... br 0)` constructs, immediately triggering Wasmtime fuel exhaustion within microseconds.

---

## 7. API Gateway & Bearer Token Authentication

The Rust Axum server safeguards all sensitive evaluation endpoints using a dedicated authentication middleware (`backend/crates/server/src/middleware.rs`).

### Endpoints
- `GET /health`: Public health check returning server status, version, and supported engines.
- `POST /api/v1/evaluate`: Protected evaluation route requiring `Authorization: Bearer <API_SECRET_KEY>`.
- `POST /api/v1/tests/generate`: Protected AI test suite generation endpoint requiring Bearer authentication.

### Authentication Enforcement Sample
```http
POST /api/v1/evaluate HTTP/1.1
Host: localhost:8080
Authorization: Bearer moodle_wasm_secret_key_2026
Content-Type: application/json

{
  "language": "python",
  "code": "a = int(input())\nb = int(input())\nprint(a + b)",
  "test_cases": [
    { "id": "tc1", "input": "10\n20\n", "expected_output": "30\n", "points": 10 }
  ],
  "fuel_limit": 10000000,
  "memory_limit_mb": 64
}
```

If the header is missing or invalid:
```json
HTTP/1.1 401 Unauthorized
{
  "error": "Unauthorized: Invalid or missing Bearer token in Authorization header."
}
```

---

## 8. Docker Compose Multi-Container Production Topology

The complete WasmGrader environment runs seamlessly via `docker-compose.yml`:

```yaml
version: '3.8'

services:
  wasm-evaluator:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: wasm_evaluator_server
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - API_SECRET_KEY=moodle_wasm_secret_key_2026
      - RUST_LOG=info
    restart: unless-stopped
    networks:
      - wasm-network

  moodle:
    image: bitnami/moodle:4.4
    container_name: moodle_lms
    ports:
      - "80:8080"
      - "443:8443"
    environment:
      - MOODLE_DATABASE_HOST=mariadb
      - MOODLE_DATABASE_PORT_NUMBER=3306
      - MOODLE_DATABASE_USER=bn_moodle
      - MOODLE_DATABASE_PASSWORD=moodle_password_2026
      - MOODLE_DATABASE_NAME=bitnami_moodle
    volumes:
      - moodle_data:/bitnami/moodle
      - moodledata_data:/bitnami/moodledata
      - ./moodle_plugin/assign/submission/wasmcode:/bitnami/moodle/mod/assign/submission/wasmcode
    depends_on:
      - mariadb
      - wasm-evaluator
    networks:
      - wasm-network

  mariadb:
    image: bitnami/mariadb:11.2
    container_name: moodle_mariadb
    environment:
      - MARIADB_USER=bn_moodle
      - MARIADB_PASSWORD=moodle_password_2026
      - MARIADB_DATABASE=bitnami_moodle
      - MARIADB_ROOT_PASSWORD=root_password_2026
    volumes:
      - mariadb_data:/bitnami/mariadb
    networks:
      - wasm-network

volumes:
  mariadb_data:
  moodle_data:
  moodledata_data:

networks:
  wasm-network:
    driver: bridge
```

---

## 9. Empirical Benchmarking, Plagiarism Detection, & Validation

### 9.1. Parallel Execution Benchmark
Benchmark tests show near-linear scaling when evaluating 100 submissions with 50 test cases each across parallel CPU threads:
![Parallel Execution Benchmark](results/figures/fig2_parallel_benchmark.png)

### 9.2. AST & Token Plagiarism Detection
WasmGrader incorporates Winnowing token hashing and AST vector cosine similarity to identify structural code copying across submissions:
![Plagiarism Heatmap](results/figures/fig_plagiarism_heatmap.png)
![Similarity Scores Distribution](results/figures/fig3_similarity_scores.png)

### 9.3. Real Execution Verification Screenshots
Real test execution outputs captured from the active test harness:
![Real Python Evaluation Test](results/figures/real_test_python_eval.png)
![Real PHP Moodle Bridge Test](results/figures/real_test_php_moodle.png)
![Real PowerShell Demo Run](results/figures/real_test_powershell_demo.png)

---

## 10. Moodle Plugin User Experience & Interface Walkthrough

### Instructor Assignment Settings
Instructors configure execution fuel limits, memory limits, and target language options directly within the assignment setup form:
![Moodle Instructor Settings](results/figures/fig_moodle_instructor_settings.png)

### AI Test Generation Modal
Instructors generate edge cases and boundary assertions with one click using the built-in LLM interface:
![Moodle AI Test Generator](results/figures/fig_moodle_ai_modal.png)

### Student Code Submission Editor
Students write and test code interactively with instant sandboxed evaluation feedback:
![Moodle Student Editor](results/figures/fig_moodle_student_editor.png)

### Automated Gradebook Synchronization
Final grades, execution times, and test breakdowns are automatically recorded into Moodle's native gradebook:
![Moodle Gradebook](results/figures/fig_moodle_gradebook.png)

---

## 11. Conclusion

**WasmGrader** delivers a robust, secure, and production-ready solution for automated programming assessment. By combining Rust, WebAssembly (WASI), and Moodle, the system eliminates host security risks, prevents infinite loops via deterministic fuel metering, achieves sub-15ms cold start latency, and accelerates educator workflows with automated AI test generation.

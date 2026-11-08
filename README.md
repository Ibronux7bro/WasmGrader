# WasmGrader 🎓⚡

**Automated Multi-Language Code Sandboxing, Assessment Engine, and AI-Driven Evaluation Architecture for Moodle via WebAssembly (WASI) and Rust**

[![License](https://img.shields.io/badge/license-MIT%20%2F%20GPL-blue.svg)](#license)
[![Rust](https://img.shields.io/badge/rust-1.75%2B-orange.svg)](https://www.rust-lang.org/)
[![WebAssembly](https://img.shields.io/badge/wasm-WASI%20Snapshot%20Preview1-purple.svg)](https://wasi.dev/)
[![Moodle](https://img.shields.io/badge/moodle-4.4%2B-red.svg)](https://moodle.org/)
[![Documentation](https://img.shields.io/badge/docs-University%20Grade-success.svg)](DOCUMENTATION.md)

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Academic Report & System Specification](#-academic-report--system-specification)
- [Key Features & Innovations](#-key-features--innovations)
- [Architecture & Software Engineering UML Models](#-architecture--software-engineering-uml-models)
- [Project Directory Layout](#-project-directory-layout)
- [Quick Start with Docker Compose](#-quick-start-with-docker-compose)
- [API Authentication & Endpoints](#-api-authentication--endpoints)
- [Verification & Automated Test Suite](#-verification--automated-test-suite)
- [License](#-license)

---

## 🚀 Overview

**WasmGrader** compiles and assesses student code submissions across multiple programming languages (**C, C++, Rust, and Python**) by compiling them to WebAssembly (WASI) bytecode and executing them within a secure, high-performance sandbox powered by **Wasmtime 21.0** and **Rust Axum**.

Unlike legacy systems that rely on slow Docker container spawns or risky OS process forks, WasmGrader guarantees:
1. **Zero-Trust Host Isolation:** Complete isolation from host sockets, disks, and child processes via in-memory virtual pipes.
2. **Deterministic Infinite Loop Protection:** Opcode-level fuel metering halts runaway loops (`Trap::OutOfFuel`) without wall-clock timer drift.
3. **Microsecond Cold Starts:** <15ms execution spin-up per test case.
4. **AI-Assisted Test Generation:** Integrated LLM synthesis for boundary assertions, edge cases, and automated Moodle grading.

---

## 📑 Academic Report & System Specification

The project includes university-grade software engineering analysis, architectural specifications, and empirical benchmark documentation:

- 📄 **Academic Word Report:** [`WasmGrader_Technical_Documentation.docx`](WasmGrader_Technical_Documentation.docx)
- 📖 **Full Markdown Specification:** [`DOCUMENTATION.md`](DOCUMENTATION.md)
- 📊 **High-Resolution Figures & UMLs (300 DPI):** Located in [`results/figures/`](results/figures/)
  - `fig1_system_architecture.png`
  - `fig2_parallel_benchmark.png`
  - `fig3_similarity_scores.png`
  - `fig_wasm_memory_layout.png`
  - `fig_plagiarism_heatmap.png`
  - `uml_use_case_diagram.png`
  - `uml_class_diagram.png`
  - `uml_sequence_evaluation.png`
  - `uml_sequence_ai.png`
  - `uml_activity_diagram.png`
  - `uml_deployment_diagram.png`
  - `uml_database_er_diagram.png`

---

## 🛡️ Key Features & Innovations

- **Deterministic Python Compilation (`compiler/src/python.rs`):** Converts Python ASTs into standard WASI modules via `wat` with stdin parsing and fuel-metered loops.
- **Axum Bearer Token Gateway (`server/src/middleware.rs`):** Protects evaluation and test generation endpoints using `Authorization: Bearer <API_SECRET_KEY>`.
- **Parallel Rayon Runner (`engine/src/pool.rs`):** Evaluates thousands of test cases in parallel across multi-core CPU threads.
- **Deep Moodle Integration (`moodle_plugin/`):** Full PHP bridge plugin supporting code editing, submission handling, and native Moodle Gradebook sync.

---

## 🏗️ Architecture & Software Engineering UML Models

```text
Student Submissions (Moodle 4.4+)
          │
          ▼  (HTTPS / cURL with Bearer Token)
Axum REST Gateway (Port 8080)
   ├── Auth Middleware (API_SECRET_KEY)
   ├── Multi-Language Compiler (Clang / Rustc / Python wat)
   └── Wasmtime 21.0 Engine (Fuel Metering + Virtual I/O)
          │
          ▼
Parallel Rayon Pool ──► Test Case Evaluation Results
          │
          ▼
Moodle Gradebook Synchronization
```

All 7 UML standard diagrams (IEEE/ISO 12207) are available in the [`results/figures/`](results/figures/) directory:
- **Use Case:** [`results/figures/uml_use_case_diagram.png`](results/figures/uml_use_case_diagram.png)
- **Class Diagram:** [`results/figures/uml_class_diagram.png`](results/figures/uml_class_diagram.png)
- **Sequence (Grading):** [`results/figures/uml_sequence_evaluation.png`](results/figures/uml_sequence_evaluation.png)
- **Sequence (AI Gen):** [`results/figures/uml_sequence_ai.png`](results/figures/uml_sequence_ai.png)
- **Activity Diagram:** [`results/figures/uml_activity_diagram.png`](results/figures/uml_activity_diagram.png)
- **Deployment Diagram:** [`results/figures/uml_deployment_diagram.png`](results/figures/uml_deployment_diagram.png)
- **Database ER Diagram:** [`results/figures/uml_database_er_diagram.png`](results/figures/uml_database_er_diagram.png)

---

## 📂 Project Directory Layout

```text
WasmGrader/
├── backend/                         # Rust Core & Evaluator Daemon
│   ├── Cargo.toml                  # Workspace Root
│   ├── Dockerfile                  # Production Multi-Stage Container
│   └── crates/
│       ├── common/                 # Shared Data Transfer Objects (DTOs)
│       ├── compiler/               # Clang, Rustc, and Python WASI Synthesizer
│       ├── engine/                 # Wasmtime Sandbox & Rayon Parallel Pool
│       ├── ai-generator/           # LLM Test Case Synthesis
│       ├── server/                 # Axum REST Gateway & Token Auth Middleware
│       └── cli/                    # Standalone Developer CLI Tool
│
├── moodle_plugin/                  # Moodle Assignment Subplugin
│   └── assign/submission/wasmcode/
│       ├── version.php             # Moodle Plugin Metadata
│       ├── settings.php            # Evaluator URL & Token Config
│       ├── locallib.php            # Grading Logic & Gradebook Integration
│       ├── classes/client.php      # Secure cURL Bridge with Bearer Token
│       └── db/install.xml          # Relational Database Schema
│
├── results/figures/                # 19 High-Resolution Visuals, Benchmarks & UMLs
├── scripts/                        # Automated Test Suites & Report Generators
├── docker-compose.yml              # Production Multi-Container Orchestration
├── DOCUMENTATION.md                # Comprehensive Markdown Academic Documentation
└── WasmGrader_Technical_Documentation.docx # Academic Word Report
```

---

## ⚡ Quick Start with Docker Compose

Deploy the complete stack (WasmGrader daemon, Moodle 4.4, and MariaDB 11.2) with a single command:

```bash
docker compose up -d
```

- **WasmGrader Evaluator API:** `http://localhost:8080`
- **Moodle LMS:** `http://localhost`
- **MariaDB Database:** `localhost:3306`

---

## 🔐 API Authentication & Endpoints

All protected endpoints enforce Bearer token authentication against `API_SECRET_KEY`:

| Method | Endpoint | Access | Header | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Public | None | Server health status |
| `POST` | `/api/v1/evaluate` | Protected | `Authorization: Bearer <API_SECRET_KEY>` | Run student code against test suite |
| `POST` | `/api/v1/tests/generate` | Protected | `Authorization: Bearer <API_SECRET_KEY>` | Synthesize test suite via AI LLM |

### Sample Evaluation Request
```bash
curl -X POST http://localhost:8080/api/v1/evaluate \
  -H "Authorization: Bearer moodle_wasm_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "a = int(input())\nb = int(input())\nprint(a + b)",
    "test_cases": [
      { "id": "tc1", "input": "5\n15\n", "expected_output": "20\n", "points": 10 }
    ],
    "fuel_limit": 10000000,
    "memory_limit_mb": 64
  }'
```

---

## 🧪 Verification & Automated Test Suite

Run the end-to-end test harnesses:

```bash
# Run local Python test harness
python scripts/test_api.py

# Run mock server for isolated Moodle bridge testing
python scripts/mock_evaluator_server.py
```

---

## 📄 License
This project is licensed under the MIT License and GNU General Public License v3.0 (GPL-3.0) for Moodle compatibility.

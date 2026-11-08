#!/usr/bin/env python3
"""
Generates complete, publication-grade UML diagrams for the WasmGrader project:
1. UML Use Case Diagram
2. UML Class Diagram
3. UML Sequence Diagram (Code Submission & Parallel Sandboxed Evaluation)
4. UML Sequence Diagram (AI Test Case Synthesis & Ground-Truth Verification)
5. UML Activity Diagram (Evaluation Lifecycle, Traps & Scoring)
6. UML Component & Deployment Architecture Diagram
7. Database Entity-Relationship (ER) Diagram
"""

import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '..', 'results', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

# -----------------------------------------------------------------
# 1. UML USE CASE DIAGRAM
# -----------------------------------------------------------------
def generate_uml_use_case():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')
    
    # System boundary box
    sys_box = plt.Rectangle((0.25, 0.05), 0.50, 0.88, facecolor='#FFFFFF', edgecolor='#1A365D', linewidth=2.5)
    ax.add_patch(sys_box)
    ax.text(0.50, 0.90, 'WasmGrader System Boundary', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    # Actors
    actors = [
        ("Student\n(Learner)", 0.10, 0.65, '#2B6CB0'),
        ("Instructor\n(Course Teacher)", 0.10, 0.25, '#2B6CB0'),
        ("LMS Admin\n(SysAdmin)", 0.90, 0.70, '#718096'),
        ("Gemini LLM\n(AI Model)", 0.90, 0.25, '#D69E2E'),
    ]

    for label, x, y, col in actors:
        ax.plot(x, y + 0.04, 'o', markersize=14, color=col)
        ax.plot([x, x], [y + 0.02, y - 0.03], color=col, linewidth=2.5)
        ax.plot([x - 0.03, x + 0.03], [y, y], color=col, linewidth=2.5)
        ax.plot([x, x - 0.02], [y - 0.03, y - 0.07], color=col, linewidth=2.5)
        ax.plot([x, x + 0.02], [y - 0.03, y - 0.07], color=col, linewidth=2.5)
        ax.text(x, y - 0.11, label, ha='center', fontsize=9.5, fontweight='bold', color=col)

    # Use Cases (Ovals)
    use_cases = [
        ("Write Code in Monaco/Ace Editor", 0.50, 0.80, '#EBF8FF', '#3182CE'),
        ("Run Immediate Public Tests (AJAX)", 0.50, 0.70, '#EBF8FF', '#3182CE'),
        ("Submit Final Solution for Grading", 0.50, 0.60, '#EBF8FF', '#3182CE'),
        ("View Sandboxed Diagnostic Logs", 0.50, 0.50, '#EBF8FF', '#3182CE'),
        ("Define Constraints (Fuel & Memory)", 0.50, 0.40, '#FEFCBF', '#D69E2E'),
        ("Synthesize Tests via AI Assistant", 0.50, 0.30, '#FEFCBF', '#D69E2E'),
        ("Dual-Verify with Reference Solution", 0.50, 0.20, '#FEFCBF', '#D69E2E'),
        ("Configure Bearer Token & Server URL", 0.50, 0.10, '#EDF2F7', '#4A5568'),
    ]

    for text, cx, cy, bg, border in use_cases:
        ax.text(cx, cy, text, ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round4,pad=0.6', facecolor=bg, edgecolor=border, linewidth=1.5))

    # Association lines
    ax.plot([0.13, 0.35], [0.65, 0.80], color='#3182CE', linewidth=1.2)
    ax.plot([0.13, 0.35], [0.65, 0.70], color='#3182CE', linewidth=1.2)
    ax.plot([0.13, 0.35], [0.65, 0.60], color='#3182CE', linewidth=1.2)
    ax.plot([0.13, 0.35], [0.65, 0.50], color='#3182CE', linewidth=1.2)

    ax.plot([0.13, 0.35], [0.25, 0.40], color='#D69E2E', linewidth=1.2)
    ax.plot([0.13, 0.35], [0.25, 0.30], color='#D69E2E', linewidth=1.2)
    ax.plot([0.13, 0.35], [0.25, 0.20], color='#D69E2E', linewidth=1.2)

    ax.plot([0.87, 0.65], [0.70, 0.10], color='#4A5568', linewidth=1.2)
    ax.plot([0.87, 0.65], [0.25, 0.30], color='#D69E2E', linewidth=1.2, linestyle='--')

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_use_case_diagram.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 2. UML CLASS DIAGRAM
# -----------------------------------------------------------------
def generate_uml_class():
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'UML Class Diagram: Core Evaluation Engine & Moodle Bridge', fontsize=14, fontweight='bold', color='#1A365D', ha='center')

    # Class Boxes Helper
    def draw_class(x, y, w, h, name, fields, methods, bg='#FFFFFF', border='#1A365D'):
        rect = plt.Rectangle((x, y), w, h, facecolor=bg, edgecolor=border, linewidth=1.8)
        ax.add_patch(rect)
        # Header
        ax.plot([x, x + w], [y + h - 0.05, y + h - 0.05], color=border, linewidth=1.2)
        ax.text(x + w/2, y + h - 0.03, name, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border)
        # Fields
        fy = y + h - 0.08
        for f in fields:
            ax.text(x + 0.015, fy, f, fontsize=8, color='#2D3748')
            fy -= 0.03
        # Separator
        ax.plot([x, x + w], [fy + 0.015, fy + 0.015], color=border, linewidth=0.8)
        # Methods
        my = fy - 0.015
        for m in methods:
            ax.text(x + 0.015, my, m, fontsize=8, color='#1A202C')
            my -= 0.03

    # WasmSandboxEngine
    draw_class(0.04, 0.55, 0.28, 0.38, "WasmSandboxEngine",
               ["- engine: Arc<wasmtime::Engine>"],
               ["+ new() -> Result<Self>",
                "+ compile_module(bytes) -> Result<Module>",
                "+ execute_test_case(mod, tc, limits)",
                "- invoke_entrypoint(store, inst)",
                "- compare_output(actual, exp) -> bool"],
               bg='#F7FAFC')

    # ParallelTestExecutor
    draw_class(0.36, 0.55, 0.28, 0.38, "ParallelTestExecutor<'a>",
               ["- engine: &'a WasmSandboxEngine",
                "- module: &'a wasmtime::Module",
                "- limits: &'a ExecutionLimits"],
               ["+ new(eng, mod, lim) -> Self",
                "+ execute_all(cases) -> Vec<TestCaseResult>"],
               bg='#F7FAFC')

    # Compiler Trait & Implementations
    draw_class(0.68, 0.55, 0.28, 0.38, "<<trait>> Compiler",
               [],
               ["+ compile(code) -> Result<CompiledOutput>"],
               bg='#EBF8FF', border='#2B6CB0')

    # Compilers
    draw_class(0.68, 0.20, 0.28, 0.30, "LanguageCompilers",
               ["+ ClangCompiler (C / C++)",
                "+ RustCompiler (Rust wasm32)",
                "+ PythonCompiler (WASI Synthesizer)"],
               ["+ get_compiler(lang) -> Box<dyn Compiler>"],
               bg='#FFFFFF')

    # Moodle PHP Bridge Classes
    draw_class(0.04, 0.12, 0.28, 0.36, "assign_submission_wasmcode",
               ["- assignment: assign",
                "- language: string",
                "- timeout_ms: int",
                "- memory_limit_mb: int"],
               ["+ get_form_elements(submission, mform)",
                "+ save(submission, data) -> bool",
                "+ view_summary(submission) -> string",
                "+ is_empty(submission) -> bool"],
               bg='#FEFCBF', border='#D69E2E')

    draw_class(0.36, 0.12, 0.28, 0.36, "assignsubmission_wasmcode\\client",
               ["- server_url: string",
                "- api_key: string"],
               ["+ evaluate(lang, code, tests, to, mem)",
                "+ generate_tests(title, desc, lang, n)",
                "- post(endpoint, data) -> array"],
               bg='#FEFCBF', border='#D69E2E')

    # Connecting Arrows
    ax.annotate('', xy=(0.36, 0.74), xytext=(0.32, 0.74), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.8))
    ax.annotate('', xy=(0.82, 0.55), xytext=(0.82, 0.50), arrowprops=dict(arrowstyle="-|>", color='#2B6CB0', lw=1.8))
    ax.annotate('', xy=(0.36, 0.30), xytext=(0.32, 0.30), arrowprops=dict(arrowstyle="->", color='#D69E2E', lw=1.8))
    ax.annotate('', xy=(0.48, 0.48), xytext=(0.48, 0.55), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.8, linestyle='--'))

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_class_diagram.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 3. UML SEQUENCE DIAGRAM (SUBMISSION & PARALLEL EVALUATION)
# -----------------------------------------------------------------
def generate_uml_sequence_evaluation():
    fig, ax = plt.subplots(figsize=(12, 8.0), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'UML Sequence Diagram: Code Submission, Sandboxing & Gradebook Sync', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    lifelines = [
        ("Student", 0.08),
        ("Moodle UI", 0.22),
        ("PHP Client", 0.38),
        ("Axum Gateway", 0.54),
        ("Compiler/Cache", 0.70),
        ("Wasmtime Sandbox", 0.88),
    ]

    for name, x in lifelines:
        ax.text(x, 0.92, name, ha='center', fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor='#E2E8F0', edgecolor='#4A5568'))
        ax.plot([x, x], [0.88, 0.05], color='#A0AEC0', linestyle='--', linewidth=1.2)

    # Messages
    msgs = [
        (0.08, 0.22, 0.83, "1. Submits code via Monaco editor", '#2B6CB0'),
        (0.22, 0.38, 0.77, "2. save(submission, data)", '#2B6CB0'),
        (0.38, 0.54, 0.71, "3. POST /api/v1/evaluate (Bearer Token)", '#E53E3E'),
        (0.54, 0.70, 0.65, "4. Check SHA-256 cache & compile WASM", '#2B6CB0'),
        (0.70, 0.54, 0.59, "5. Return compiled .wasm bytecode", '#38A169'),
        (0.54, 0.88, 0.53, "6. Execute test suite in parallel (Rayon)", '#2B6CB0'),
        (0.88, 0.88, 0.46, "7. Enforce Fuel metering & Memory bounds", '#D69E2E'),
        (0.88, 0.54, 0.39, "8. Return TestCaseResult[] (Outputs/Times)", '#38A169'),
        (0.54, 0.38, 0.33, "9. Return EvaluationResponse (JSON)", '#38A169'),
        (0.38, 0.22, 0.26, "10. Update Moodle Gradebook & record", '#2B6CB0'),
        (0.22, 0.08, 0.18, "11. Display score percentage & terminal report", '#38A169'),
    ]

    for x1, x2, y, text, col in msgs:
        if x1 == x2:
            # Self call loop
            ax.plot([x1, x1 + 0.05, x1 + 0.05, x1], [y, y, y - 0.03, y - 0.03], color=col, linewidth=1.5)
            ax.text(x1 + 0.06, y - 0.015, text, fontsize=8, color=col, va='center')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.5))
            mid = (x1 + x2) / 2
            ax.text(mid, y + 0.015, text, fontsize=8, color=col, ha='center')

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_sequence_evaluation.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 4. UML SEQUENCE DIAGRAM (AI TEST CASE GENERATION)
# -----------------------------------------------------------------
def generate_uml_sequence_ai():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'UML Sequence Diagram: AI Test Case Synthesis & Reference Verification', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    lifelines = [
        ("Instructor", 0.10),
        ("Moodle Modal", 0.28),
        ("Axum Gateway", 0.50),
        ("Gemini AI Client", 0.72),
        ("Wasmtime Verifier", 0.90),
    ]

    for name, x in lifelines:
        ax.text(x, 0.92, name, ha='center', fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEFCBF', edgecolor='#D69E2E'))
        ax.plot([x, x], [0.88, 0.05], color='#A0AEC0', linestyle='--', linewidth=1.2)

    msgs = [
        (0.10, 0.28, 0.81, "1. Click 'Auto-Generate with AI' & enter count", '#2B6CB0'),
        (0.28, 0.50, 0.73, "2. POST /api/v1/tests/generate (Title, Intro, RefSol)", '#E53E3E'),
        (0.50, 0.72, 0.65, "3. Formulate Prompt with strict JSON Schema", '#D69E2E'),
        (0.72, 0.72, 0.57, "4. LLM Generation (Happy path, boundary, hidden)", '#D69E2E'),
        (0.72, 0.50, 0.49, "5. Return structured TestCase[] payload", '#38A169'),
        (0.50, 0.90, 0.41, "6. Run Reference Solution against generated inputs", '#2B6CB0'),
        (0.90, 0.50, 0.33, "7. Align expected_output with ground truth", '#38A169'),
        (0.50, 0.28, 0.25, "8. Return verified test cases to Moodle", '#38A169'),
        (0.28, 0.10, 0.16, "9. Render preview modal with Public/Secret tags", '#2B6CB0'),
    ]

    for x1, x2, y, text, col in msgs:
        if x1 == x2:
            ax.plot([x1, x1 + 0.05, x1 + 0.05, x1], [y, y, y - 0.03, y - 0.03], color=col, linewidth=1.5)
            ax.text(x1 + 0.06, y - 0.015, text, fontsize=8, color=col, va='center')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.5))
            mid = (x1 + x2) / 2
            ax.text(mid, y + 0.015, text, fontsize=8, color=col, ha='center')

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_sequence_ai.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 5. UML ACTIVITY DIAGRAM (SANDBOX EXECUTION LIFECYCLE)
# -----------------------------------------------------------------
def generate_uml_activity():
    fig, ax = plt.subplots(figsize=(10, 9.0), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'UML Activity Diagram: Evaluation Pipeline, Traps & Scoring', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    # Initial Node
    ax.plot(0.50, 0.93, 'o', markersize=14, color='#1A365D')

    # Action Boxes & Diamonds Helper
    def draw_action(y, text, bg='#EBF8FF', border='#3182CE'):
        ax.text(0.50, y, text, ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.5', facecolor=bg, edgecolor=border, linewidth=1.5))

    def draw_diamond(y, text):
        ax.text(0.50, y, text, ha='center', va='center', fontsize=8.5,
                bbox=dict(boxstyle='square,pad=0.4', facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5))

    # Flow
    steps = [
        (0.86, "Ingest Evaluation Request (Language, Source Code, TestCases)"),
        (0.79, "Validate API Bearer Token (Auth Middleware)"),
        (0.71, "Query SHA-256 Compilation Cache"),
        (0.63, "Compile Code to wasm32-wasip1 (LLVM/Rustc/Python)"),
        (0.55, "Configure Wasmtime Store: Fuel Metering & Memory Ceiling"),
        (0.47, "Spawn Rayon Parallel Worker Pool for Test Cases"),
        (0.39, "Execute WASM Instance inside Isolated WASI Context"),
    ]

    for y, text in steps:
        draw_action(y, text)

    # Decision on Execution Outcome
    draw_diamond(0.30, "Trap Encountered?")

    # Outcomes
    ax.text(0.18, 0.21, "Trap::OutOfFuel\n(TimeLimitExceeded)", ha='center', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E'))
    ax.text(0.50, 0.21, "Trap::MemoryOutOfBounds\n(MemoryLimitExceeded)", ha='center', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E'))
    ax.text(0.82, 0.21, "Normal Exit (proc_exit)\n(Compare Stdout Output)", ha='center', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#C6F6D5', edgecolor='#38A169'))

    draw_action(0.11, "Aggregate Results & Calculate Weighted Score Percentage")

    # Final Node (Bullseye)
    ax.plot(0.50, 0.04, 'o', markersize=14, color='#1A365D')
    ax.plot(0.50, 0.04, 'o', markersize=8, color='#FFFFFF')
    ax.plot(0.50, 0.04, 'o', markersize=4, color='#1A365D')

    # Flow arrows
    y_coords = [0.93, 0.86, 0.79, 0.71, 0.63, 0.55, 0.47, 0.39, 0.30]
    for i in range(len(y_coords) - 1):
        ax.annotate('', xy=(0.50, y_coords[i+1] + 0.025), xytext=(0.50, y_coords[i] - 0.025),
                    arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.5))

    # Branch arrows from diamond
    ax.annotate('', xy=(0.18, 0.24), xytext=(0.42, 0.30), arrowprops=dict(arrowstyle="->", color='#E53E3E', lw=1.2))
    ax.text(0.28, 0.28, "Timeout", fontsize=7.5, color='#E53E3E')

    ax.annotate('', xy=(0.50, 0.24), xytext=(0.50, 0.27), arrowprops=dict(arrowstyle="->", color='#E53E3E', lw=1.2))
    ax.text(0.52, 0.25, "OOM", fontsize=7.5, color='#E53E3E')

    ax.annotate('', xy=(0.82, 0.24), xytext=(0.58, 0.30), arrowprops=dict(arrowstyle="->", color='#38A169', lw=1.2))
    ax.text(0.70, 0.28, "Success", fontsize=7.5, color='#38A169')

    # Rejoin to aggregate
    ax.plot([0.18, 0.18, 0.50], [0.18, 0.14, 0.14], color='#1A365D', lw=1.2)
    ax.plot([0.82, 0.82, 0.50], [0.18, 0.14, 0.14], color='#1A365D', lw=1.2)
    ax.annotate('', xy=(0.50, 0.13), xytext=(0.50, 0.17), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.2))
    ax.annotate('', xy=(0.50, 0.06), xytext=(0.50, 0.09), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.5))

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_activity_diagram.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 6. UML COMPONENT & DEPLOYMENT DIAGRAM
# -----------------------------------------------------------------
def generate_uml_deployment():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'UML Component & Deployment Diagram (Docker Swarm / Compose Host)', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    # Docker Host Box
    host_box = plt.Rectangle((0.05, 0.05), 0.90, 0.88, facecolor='#F8FAFC', edgecolor='#1A365D', linewidth=2.5)
    ax.add_patch(host_box)
    ax.text(0.08, 0.89, '<<Node>> Docker Host Server (Linux / Windows Host)', fontsize=11, fontweight='bold', color='#1A365D')

    # Container 1: Moodle Server
    c1 = plt.Rectangle((0.08, 0.45), 0.38, 0.40, facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=2)
    ax.add_patch(c1)
    ax.text(0.27, 0.81, '<<Container>> moodle-server\n(bitnami/moodle:4.4)', fontsize=10, fontweight='bold', color='#2B6CB0', ha='center')
    ax.text(0.27, 0.68, '<<Component>> Moodle Core PHP Engine', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.27, 0.55, '<<Component>> assignsubmission_wasmcode\n(Subplugin & Monaco Editor)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))

    # Container 2: MariaDB
    c2 = plt.Rectangle((0.08, 0.10), 0.38, 0.28, facecolor='#EDF2F7', edgecolor='#4A5568', linewidth=2)
    ax.add_patch(c2)
    ax.text(0.27, 0.33, '<<Container>> moodle-mariadb\n(bitnami/mariadb:11.2)', fontsize=10, fontweight='bold', color='#2D3748', ha='center')
    ax.text(0.27, 0.20, '<<Database>> bitnami_moodle\n(mdl_assignsubmission_wasmcode)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))

    # Container 3: Rust WASM Evaluator
    c3 = plt.Rectangle((0.54, 0.10), 0.38, 0.75, facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=2)
    ax.add_patch(c3)
    ax.text(0.73, 0.81, '<<Container>> moodle-wasm-evaluator\n(Debian Bullseye Slim)', fontsize=10, fontweight='bold', color='#C53030', ha='center')
    ax.text(0.73, 0.69, '<<Component>> Axum REST API Gateway\n(:8080 | Bearer Token Auth)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.73, 0.55, '<<Component>> Compilers (clang, rustc, python)\n& SHA-256 Content Cache', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.73, 0.40, '<<Component>> Wasmtime Sandboxing Engine\n(Fuel Limits & Linear Memory Bounds)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.73, 0.24, '<<Component>> Rayon Parallel Worker Pool\n(Multi-Core Concurrent Execution)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))

    # Network connections
    ax.annotate('', xy=(0.54, 0.65), xytext=(0.46, 0.65), arrowprops=dict(arrowstyle="<->", color='#3182CE', lw=2))
    ax.text(0.50, 0.68, 'HTTP/REST\n:8080', fontsize=8, ha='center', color='#3182CE', fontweight='bold')

    ax.annotate('', xy=(0.27, 0.38), xytext=(0.27, 0.45), arrowprops=dict(arrowstyle="<->", color='#4A5568', lw=2))
    ax.text(0.31, 0.41, 'TCP:3306', fontsize=8, color='#4A5568', fontweight='bold')

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_deployment_diagram.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

# -----------------------------------------------------------------
# 7. DATABASE ENTITY-RELATIONSHIP (ER) DIAGRAM
# -----------------------------------------------------------------
def generate_uml_database_er():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.axis('off')
    ax.text(0.50, 0.98, 'Database Entity-Relationship (ER) Diagram: Moodle Schema', fontsize=13, fontweight='bold', color='#1A365D', ha='center')

    def draw_entity(x, y, w, h, name, pk_fields, other_fields):
        rect = plt.Rectangle((x, y), w, h, facecolor='#FFFFFF', edgecolor='#1A365D', linewidth=1.8)
        ax.add_patch(rect)
        # Header
        ax.plot([x, x + w], [y + h - 0.05, y + h - 0.05], color='#1A365D', linewidth=1.2)
        ax.text(x + w/2, y + h - 0.03, name, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1A365D')
        # PKs
        fy = y + h - 0.08
        for pk in pk_fields:
            ax.text(x + 0.015, fy, f"🔑 {pk}", fontsize=8, fontweight='bold', color='#2B6CB0')
            fy -= 0.035
        # Separator
        ax.plot([x, x + w], [fy + 0.015, fy + 0.015], color='#CBD5E0', linewidth=0.8)
        # Fields
        for of in other_fields:
            ax.text(x + 0.015, fy - 0.01, of, fontsize=8, color='#4A5568')
            fy -= 0.032

    # Entities
    draw_entity(0.05, 0.55, 0.25, 0.35, "mdl_course",
                ["id: INT(10)"],
                ["fullname: VARCHAR(254)", "shortname: VARCHAR(100)", "summary: TEXT", "timecreated: INT(10)"])

    draw_entity(0.38, 0.55, 0.25, 0.35, "mdl_assign",
                ["id: INT(10)"],
                ["course: INT(10) [FK]", "name: VARCHAR(255)", "intro: TEXT", "grade: BIGINT(10)", "duedate: INT(10)"])

    draw_entity(0.70, 0.55, 0.25, 0.35, "mdl_assign_submission",
                ["id: INT(10)"],
                ["assignment: INT(10) [FK]", "userid: INT(10) [FK]", "status: VARCHAR(10)", "timemodified: INT(10)"])

    draw_entity(0.38, 0.08, 0.28, 0.38, "mdl_assignsubmission_wasmcode",
                ["id: INT(10)"],
                ["assignment: INT(10) [FK]",
                 "submission: INT(10) [FK]",
                 "source_code: LONGTEXT",
                 "grade: DECIMAL(10,5)",
                 "evaluation_result: LONGTEXT",
                 "timecreated: INT(10)",
                 "timemodified: INT(10)"])

    draw_entity(0.70, 0.08, 0.25, 0.38, "mdl_grade_grades",
                ["id: INT(10)"],
                ["itemid: INT(10) [FK]", "userid: INT(10) [FK]", "rawgrade: DECIMAL(10,5)", "feedback: LONGTEXT", "timemodified: INT(10)"])

    # Relationships
    ax.annotate('', xy=(0.38, 0.72), xytext=(0.30, 0.72), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.5))
    ax.text(0.34, 0.74, "1 : N", fontsize=8, color='#1A365D', fontweight='bold')

    ax.annotate('', xy=(0.70, 0.72), xytext=(0.63, 0.72), arrowprops=dict(arrowstyle="->", color='#1A365D', lw=1.5))
    ax.text(0.66, 0.74, "1 : N", fontsize=8, color='#1A365D', fontweight='bold')

    ax.annotate('', xy=(0.52, 0.46), xytext=(0.75, 0.55), arrowprops=dict(arrowstyle="->", color='#2B6CB0', lw=1.5))
    ax.text(0.66, 0.50, "1 : 1", fontsize=8, color='#2B6CB0', fontweight='bold')

    ax.annotate('', xy=(0.82, 0.46), xytext=(0.82, 0.55), arrowprops=dict(arrowstyle="->", color='#2B6CB0', lw=1.5))
    ax.text(0.84, 0.50, "1 : 1", fontsize=8, color='#2B6CB0', fontweight='bold')

    fig.tight_layout()
    out = os.path.join(FIG_DIR, 'uml_database_er_diagram.png')
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Generated: {out}")

if __name__ == '__main__':
    generate_uml_use_case()
    generate_uml_class()
    generate_uml_sequence_evaluation()
    generate_uml_sequence_ai()
    generate_uml_activity()
    generate_uml_deployment()
    generate_uml_database_er()
    print("All 7 UML diagrams generated successfully.")

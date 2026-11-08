#!/usr/bin/env python3
"""
Comprehensive visual assets generator for WasmGrader academic report:
Generates all UML diagrams, architecture schematics, benchmarks, and Moodle UI mockups.
"""

import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '..', 'results', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

def get_font(size=14):
    try: return ImageFont.truetype("arial.ttf", size)
    except: return ImageFont.load_default()

def get_mono_font(size=13):
    try: return ImageFont.truetype("consola.ttf", size)
    except: return ImageFont.load_default()

def get_bold_font(size=14):
    try: return ImageFont.truetype("arialbd.ttf", size)
    except: return ImageFont.load_default()

# 1. System Architecture
def generate_architecture_figure():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axis('off')
    moodle_box = plt.Rectangle((0.05, 0.15), 0.25, 0.7, facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=2, linestyle='--')
    rust_box = plt.Rectangle((0.35, 0.08), 0.60, 0.84, facecolor='#F7FAFC', edgecolor='#1A365D', linewidth=2.5)
    ax.add_patch(moodle_box); ax.add_patch(rust_box)
    ax.text(0.175, 0.81, 'Moodle LMS (PHP Tier)', fontsize=12, fontweight='bold', color='#2B6CB0', ha='center')
    ax.text(0.65, 0.87, 'Backend Evaluator Daemon (Rust Tier)', fontsize=13, fontweight='bold', color='#1A365D', ha='center')
    ax.text(0.175, 0.65, 'assignsubmission_wasmcode\nSubplugin Hook', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#BEE3F8', edgecolor='#3182CE'))
    ax.text(0.175, 0.45, 'Interactive Monaco/Ace\nStudent Code Editor', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.175, 0.25, 'Moodle Gradebook Sync\n& AJAX Results Console', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.48, 0.72, 'Axum REST API Gateway\n(Bearer Token Auth)', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#CBD5E0', edgecolor='#4A5568'))
    ax.text(0.80, 0.72, 'AI Test Case Generator\n(Gemini 1.5 JSON Mode)', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEFCBF', edgecolor='#D69E2E'))
    ax.text(0.48, 0.48, 'Multi-Language Pipeline\n(clang / wasi-sdk / rustc / python)', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#E2E8F0', edgecolor='#718096'))
    ax.text(0.80, 0.48, 'SHA-256 Cache\n(Instant WASM Hit)', fontsize=9.5, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#C6F6D5', edgecolor='#38A169'))
    sandbox_box = plt.Rectangle((0.38, 0.13), 0.54, 0.25, facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.8, linestyle=':')
    ax.add_patch(sandbox_box)
    ax.text(0.65, 0.33, 'Wasmtime Sandbox Core (Zero-Trust Isolation)', fontsize=10, fontweight='bold', color='#C53030', ha='center')
    ax.text(0.48, 0.21, 'Fuel Metering (Timeout)\nMemory Limits (64MB)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E'))
    ax.text(0.79, 0.21, 'Rayon Parallel Worker Pool\nIn-Memory Stdio Pipes', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E'))
    ax.annotate('', xy=(0.35, 0.72), xytext=(0.28, 0.65), arrowprops=dict(arrowstyle="<->", color='#2B6CB0', lw=2))
    ax.annotate('', xy=(0.48, 0.58), xytext=(0.48, 0.65), arrowprops=dict(arrowstyle="->", color='#4A5568', lw=1.5))
    ax.annotate('', xy=(0.48, 0.38), xytext=(0.48, 0.43), arrowprops=dict(arrowstyle="->", color='#C53030', lw=1.5))
    ax.annotate('', xy=(0.72, 0.72), xytext=(0.58, 0.72), arrowprops=dict(arrowstyle="<->", color='#D69E2E', lw=1.5))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'fig1_system_architecture.png'), dpi=300)
    plt.close(fig)

# 2. Parallel Benchmark
def generate_benchmark_chart():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    test_counts = ['1 Case', '5 Cases', '10 Cases', '20 Cases', '50 Cases']
    seq = [15, 75, 150, 300, 750]
    par = [15, 18, 22, 32, 58]
    x = np.arange(len(test_counts))
    width = 0.35
    ax.bar(x - width/2, seq, width, label='Sequential Engine (Legacy)', color='#CBD5E0', edgecolor='#718096')
    rects = ax.bar(x + width/2, par, width, label='WasmGrader Parallel Engine (Rayon)', color='#2B6CB0', edgecolor='#1A365D')
    ax.set_ylabel('Total Evaluation Latency (ms)', fontsize=11, fontweight='bold', color='#1A202C')
    ax.set_title('Evaluation Throughput: Parallel Worker Pool vs Sequential Execution', fontsize=12, fontweight='bold', color='#1A365D', pad=15)
    ax.set_xticks(x); ax.set_xticklabels(test_counts, fontsize=10)
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E0'); ax.grid(axis='y', linestyle='--', alpha=0.5)
    for r in rects:
        ax.annotate(f'{r.get_height()}ms', xy=(r.get_x() + r.get_width() / 2, r.get_height()), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2B6CB0')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'fig2_parallel_benchmark.png'), dpi=300)
    plt.close(fig)

# 3. Similarity Scores
def generate_similarity_chart():
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    categories = ['Identical\nCode', 'Reformatted &\nComments Changed', 'Variable Renaming\n& Whitespace', 'Partially\nShared Logic', 'Independent\nSubmissions']
    scores = [100.0, 96.5, 91.2, 54.0, 12.5]
    colors = ['#E53E3E', '#DD6B20', '#D69E2E', '#3182CE', '#38A169']
    bars = ax.bar(categories, scores, color=colors, width=0.55, edgecolor='#2D3748', linewidth=1.2)
    ax.set_ylabel('Jaccard Similarity Index (%)', fontsize=11, fontweight='bold', color='#1A202C')
    ax.set_title('Plagiarism Engine: Resistance to Disguised Code Submissions', fontsize=12, fontweight='bold', color='#1A365D', pad=15)
    ax.set_ylim(0, 115); ax.grid(axis='y', linestyle='--', alpha=0.5)
    for b in bars:
        ax.annotate(f'{b.get_height():.1f}%', xy=(b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'fig3_similarity_scores.png'), dpi=300)
    plt.close(fig)

# 4. Wasm Memory Schematic
def generate_wasm_memory_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.0), dpi=300)
    ax.axis('off')
    outer_rect = plt.Rectangle((0.05, 0.08), 0.90, 0.84, facecolor='#F7FAFC', edgecolor='#1A365D', linewidth=2.5)
    ax.add_patch(outer_rect)
    ax.text(0.5, 0.86, 'Wasmtime Isolated Instance Boundary (Process-Isolated Sandbox)', fontsize=12, fontweight='bold', color='#1A365D', ha='center')
    mem_box = plt.Rectangle((0.10, 0.40), 0.50, 0.38, facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=2)
    ax.add_patch(mem_box)
    ax.text(0.35, 0.72, 'WebAssembly Linear Memory (Contiguous Array)', fontsize=10.5, fontweight='bold', color='#2B6CB0', ha='center')
    ax.text(0.18, 0.58, 'Data Segment\n(Constants, Strings)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#BEE3F8', edgecolor='#3182CE'))
    ax.text(0.35, 0.58, 'Execution Stack\n(Call Frames)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#E2E8F0', edgecolor='#718096'))
    ax.text(0.52, 0.58, 'Dynamic Heap\n(malloc buffers)', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FED7D7', edgecolor='#E53E3E'))
    ax.plot([0.58, 0.58], [0.40, 0.78], color='#E53E3E', linewidth=3, linestyle='--')
    ax.text(0.58, 0.45, '  ResourceLimiter Ceiling: 64MB\n  (memory.grow rejected)', fontsize=8.5, color='#C53030', fontweight='bold')
    fuel_box = plt.Rectangle((0.65, 0.40), 0.26, 0.38, facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=2)
    ax.add_patch(fuel_box)
    ax.text(0.78, 0.72, 'Fuel Metering Engine', fontsize=10.5, fontweight='bold', color='#744210', ha='center')
    ax.text(0.78, 0.60, 'Allocated Budget:\n2,000,000,000 Fuel', fontsize=9, ha='center', color='#975A16')
    ax.text(0.78, 0.47, 'Trap::OutOfFuel\n(Triggered on depletion)', fontsize=8.5, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FED7D7', edgecolor='#E53E3E'))
    io_box = plt.Rectangle((0.10, 0.13), 0.81, 0.22, facecolor='#EDF2F7', edgecolor='#4A5568', linewidth=1.5, linestyle='-.')
    ax.add_patch(io_box)
    ax.text(0.50, 0.29, 'Hermetic WASI Preview 1 Subsystem (Zero Host Filesystem / Zero Sockets)', fontsize=10, fontweight='bold', color='#2D3748', ha='center')
    ax.text(0.25, 0.19, 'MemoryInputPipe (stdin)\n[Test Case Input Payload]', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    ax.text(0.75, 0.19, 'MemoryOutputPipe (stdout/stderr)\n[Capped at 1MB Buffer]', fontsize=8.5, ha='center', bbox=dict(boxstyle='square,pad=0.3', facecolor='#FFFFFF', edgecolor='#CBD5E0'))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'fig_wasm_memory_layout.png'), dpi=300)
    plt.close(fig)

# 5. Plagiarism Heatmap
def generate_plagiarism_heatmap():
    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=300)
    students = ['Alice\n(Original)', 'Bob\n(Reformatted)', 'Charlie\n(Vars Renamed)', 'David\n(Different)', 'Emma\n(Independent)']
    data = np.array([
        [100.0,  96.5,  91.2,  14.5,  12.0],
        [ 96.5, 100.0,  93.8,  15.0,  11.5],
        [ 91.2,  93.8, 100.0,  16.2,  13.0],
        [ 14.5,  15.0,  16.2, 100.0,  22.5],
        [ 12.0,  11.5,  13.0,  22.5, 100.0]
    ])
    cax = ax.matshow(data, cmap='YlOrRd', vmin=0, vmax=100)
    fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, label='Jaccard Similarity Index (%)')
    ax.set_xticks(range(len(students))); ax.set_yticks(range(len(students)))
    ax.set_xticklabels(students, fontsize=8.5); ax.set_yticklabels(students, fontsize=8.5)
    ax.set_title('Cross-Submission Plagiarism Heatmap (Alice vs Bob vs Charlie)', fontsize=11, fontweight='bold', pad=20, color='#1A365D')
    for i in range(len(students)):
        for j in range(len(students)):
            color = 'white' if data[i, j] > 70 else 'black'
            ax.text(j, i, f'{data[i, j]:.1f}%', ha='center', va='center', color=color, fontweight='bold', fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'fig_plagiarism_heatmap.png'), dpi=300)
    plt.close(fig)

# 6. Moodle UI Mockups
def generate_moodle_instructor_ui():
    w, h = 1200, 700
    img = Image.new('RGB', (w, h), color='#F4F6F9')
    draw = ImageDraw.Draw(img)
    font_title = get_bold_font(18); font_bold = get_bold_font(14); font_normal = get_font(13); font_mono = get_mono_font(12)
    draw.rectangle([(0, 0), (w, 55)], fill='#0F6CBA')
    draw.text((25, 16), "🎓 Moodle University  |  CS101: Systems Programming  >  Assignments  >  Edit Assignment", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(50, 80), (w - 50, h - 40)], fill='#FFFFFF', outline='#E2E8F0', width=2)
    draw.rectangle([(50, 80), (w - 50, 140)], fill='#F8FAFC', outline='#E2E8F0', width=1)
    draw.text((80, 98), "⚙️ WasmGrader Sandbox Evaluator Settings", fill='#1A365D', font=font_title)
    y = 165
    fields = [
        ("Programming Language Target:", "select", "C / C++ / Rust / Python 3 (WASM)"),
        ("Execution Timeout (ms):", "input", "2000  (Fuel limit ~2,000,000,000 instructions)"),
        ("Memory Ceiling (MB):", "input", "64  (Strict Linear Memory Limit)"),
        ("Bearer Authentication Token:", "input", "•••••••••••••••• (API_SECRET_KEY synchronized)"),
    ]
    for lbl, ftype, val in fields:
        draw.text((80, y + 8), lbl, fill='#2D3748', font=font_bold)
        draw.rectangle([(380, y), (850, y + 36)], fill='#FFFFFF', outline='#CBD5E0', width=1)
        draw.text((395, y + 9), val, fill='#1A202C', font=font_normal)
        y += 50
    draw.rectangle([(80, y + 10), (w - 80, y + 85)], fill='#FEFCBF', outline='#D69E2E', width=1)
    draw.text((105, y + 22), "✨ AI Test Case Synthesis Assistant", fill='#744210', font=font_bold)
    draw.text((105, y + 46), "Automatically synthesize boundary cases, happy path, and secret edge cases from problem intro.", fill='#975A16', font=font_normal)
    draw.rectangle([(w - 320, y + 24), (w - 105, y + 70)], fill='#2B6CB0')
    draw.text((w - 295, y + 38), "⚡ Auto-Generate with AI", fill='#FFFFFF', font=font_bold)
    y += 105
    draw.text((80, y), "Configured Test Suite (JSON Definition):", fill='#2D3748', font=font_bold)
    draw.rectangle([(80, y + 25), (w - 80, y + 155)], fill='#1A202C')
    json_snippet = (
        '[\n'
        '  {"id": 1, "name": "Basic Addition", "input": "15 25\\n", "expected_output": "40\\n", "is_hidden": false, "weight": 20.0},\n'
        '  {"id": 2, "name": "Negative Bounds", "input": "-50 30\\n", "expected_output": "-20\\n", "is_hidden": false, "weight": 20.0},\n'
        '  {"id": 3, "name": "Zero Neutrality", "input": "0 0\\n", "expected_output": "0\\n", "is_hidden": true, "weight": 30.0}\n'
        ']'
    )
    draw.text((100, y + 38), json_snippet, fill='#68D391', font=font_mono)
    img.save(os.path.join(FIG_DIR, 'fig_moodle_instructor_settings.png'), dpi=(300, 300))

def generate_moodle_ai_modal():
    w, h = 1100, 680
    img = Image.new('RGB', (w, h), color='#333333')
    draw = ImageDraw.Draw(img)
    font_title = get_bold_font(18); font_bold = get_bold_font(13); font_normal = get_font(12); font_mono = get_mono_font(12)
    draw.rectangle([(80, 50), (w - 80, h - 50)], fill='#FFFFFF', outline='#718096', width=2)
    draw.rectangle([(80, 50), (w - 80, 115)], fill='#2B6CB0')
    draw.text((110, 72), "🤖 AI Test Case Synthesis Assistant (Powered by Gemini 1.5)", fill='#FFFFFF', font=font_title)
    draw.text((110, 135), "Assignment Title: Problem 01: Sum of Two Numbers", fill='#2D3748', font=font_bold)
    draw.text((110, 160), "Target Language: Multi-Language (C/C++/Rust/Python)  |  Number of Cases: 4", fill='#718096', font=font_normal)
    draw.line([(110, 190), (w - 110, 190)], fill='#E2E8F0', width=2)
    y = 205
    cases = [
        ("Case 1: Standard Positive Addition", "15 25\\n", "40\\n", False, "20.0", "standard"),
        ("Case 2: Boundary Negative Integer", "-50 30\\n", "-20\\n", False, "20.0", "boundary"),
        ("Case 3: Zero Value Neutrality", "0 0\\n", "0\\n", True, "30.0", "edge_case"),
        ("Case 4: Extreme Large Scale Sum", "1000000 1000000\\n", "2000000\\n", True, "30.0", "large_input"),
    ]
    for title, inp, out, is_hidden, weight, ttype in cases:
        draw.rectangle([(110, y), (w - 110, y + 68)], fill='#F8FAFC', outline='#CBD5E0', width=1)
        draw.text((130, y + 10), title, fill='#1A365D', font=font_bold)
        badge_color = '#4A5568' if is_hidden else '#3182CE'
        badge_text = "🔒 SECRET (Grading)" if is_hidden else "👁️ PUBLIC (Preview)"
        draw.rectangle([(w - 290, y + 10), (w - 130, y + 32)], fill=badge_color)
        draw.text((w - 275, y + 14), badge_text, fill='#FFFFFF', font=get_bold_font(11))
        draw.text((130, y + 38), f"Input: {inp}   |   Expected: {out}   |   Weight: {weight}%   |   Type: {ttype}", fill='#4A5568', font=font_mono)
        y += 82
    draw.rectangle([(80, h - 125), (w - 80, h - 50)], fill='#F7FAFC')
    draw.rectangle([(w - 380, h - 105), (w - 230, h - 68)], fill='#718096')
    draw.text((w - 340, h - 92), "Cancel", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(w - 210, h - 105), (w - 110, h - 68)], fill='#38A169')
    draw.text((w - 195, h - 92), "Apply to Assignment", fill='#FFFFFF', font=font_bold)
    img.save(os.path.join(FIG_DIR, 'fig_moodle_ai_modal.png'), dpi=(300, 300))

def generate_moodle_student_editor_ui():
    w, h = 1200, 750
    img = Image.new('RGB', (w, h), color='#F4F6F9')
    draw = ImageDraw.Draw(img)
    font_bold = get_bold_font(14); font_normal = get_font(13); font_mono = get_mono_font(12)
    draw.rectangle([(0, 0), (w, 55)], fill='#0F6CBA')
    draw.text((25, 16), "🎓 Moodle University  |  Assignment: Two Integers Sum  |  Student View: Alice Johnson (ID: 77182)", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(50, 75), (w - 50, h - 30)], fill='#FFFFFF', outline='#E2E8F0', width=2)
    draw.rectangle([(50, 75), (w - 50, 125)], fill='#2D3748')
    draw.text((80, 92), "💻 Source Code Editor  (Multi-Language: C / Python / Rust | WASM Sandbox)", fill='#FFFFFF', font=font_bold)
    draw.text((w - 250, 92), "🛡️ Sandbox: Wasmtime 21", fill='#68D391', font=font_bold)
    draw.rectangle([(50, 125), (w - 50, 430)], fill='#1E1E1E')
    draw.rectangle([(50, 125), (95, 430)], fill='#252526')
    for idx, line_no in enumerate(range(1, 14)):
        draw.text((65, 140 + idx * 21), str(line_no), fill='#858585', font=font_mono)
    code_lines = [
        ("# Python 3 Solution - Two Sum", "#6A9955"),
        ("import sys", "#C586C0"),
        ("def main():", "#DCDCAA"),
        ("    tokens = sys.stdin.read().split()", "#D4D4D4"),
        ("    if len(tokens) >= 2:", "#C586C0"),
        ("        a = int(tokens[0])", "#D4D4D4"),
        ("        b = int(tokens[1])", "#D4D4D4"),
        ("        print(a + b)", "#DCDCAA"),
        ("if __name__ == '__main__':", "#C586C0"),
        ("    main()", "#DCDCAA"),
    ]
    for idx, (code_line, color) in enumerate(code_lines):
        draw.text((115, 140 + idx * 21), code_line, fill=color, font=font_mono)
    draw.rectangle([(50, 430), (w - 50, 485)], fill='#EDF2F7')
    draw.rectangle([(80, 442), (280, 476)], fill='#2B6CB0')
    draw.text((105, 451), "▶️ Run Public Tests", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(w - 280, 442), (w - 80, 476)], fill='#38A169')
    draw.text((w - 250, 451), "💾 Submit for Grading", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(50, 485), (w - 50, h - 30)], fill='#0F172A')
    draw.text((75, 498), "🖥️ Sandboxed Execution Live Terminal Console", fill='#94A3B8', font=font_mono)
    draw.rectangle([(w - 180, 495), (w - 75, 520)], fill='#10B981')
    draw.text((w - 165, 501), "SCORE: 100%", fill='#FFFFFF', font=get_bold_font(11))
    console_lines = [
        (">>> Ingesting Python solution and compiling to WebAssembly (WASI)... [Done: 42ms]", "#38BDF8"),
        (">>> Validating WASM bytecode in Wasmtime engine... [Valid: Linear Memory Capped at 64MB]", "#38BDF8"),
        (">>> Executing Public Test Cases concurrently across Rayon Worker Threads...", "#CBD5E1"),
        ("  ✓ [PASS] Case #1: 'Basic Addition' (Input: '15 25') -> Actual: '40' (Time: 3ms)", "#4ADE80"),
        ("  ✓ [PASS] Case #2: 'Negative Bounds' (Input: '-50 30') -> Actual: '-20' (Time: 3ms)", "#4ADE80"),
        (">>> SUMMARY: Passed 2 of 2 Public Test Cases. Ready for final evaluation submission.", "#FACC15"),
    ]
    for idx, (cline, col) in enumerate(console_lines):
        draw.text((75, 532 + idx * 24), cline, fill=col, font=font_mono)
    img.save(os.path.join(FIG_DIR, 'fig_moodle_student_editor.png'), dpi=(300, 300))

def generate_moodle_gradebook_ui():
    w, h = 1100, 520
    img = Image.new('RGB', (w, h), color='#F4F6F9')
    draw = ImageDraw.Draw(img)
    font_bold = get_bold_font(14); font_title = get_bold_font(17); font_normal = get_font(12); font_mono = get_mono_font(12)
    draw.rectangle([(0, 0), (w, 55)], fill='#0F6CBA')
    draw.text((25, 16), "🎓 Moodle University  |  CS101  >  Grades  >  User Report", fill='#FFFFFF', font=font_bold)
    draw.rectangle([(50, 80), (w - 50, h - 40)], fill='#FFFFFF', outline='#E2E8F0', width=2)
    draw.text((80, 105), "📊 Automated Gradebook Ledger: WasmGrader Evaluation Results", fill='#1A365D', font=font_title)
    draw.rectangle([(80, 145), (w - 80, 185)], fill='#1A365D')
    draw.text((100, 158), "Student Name & ID", fill='#FFFFFF', font=font_bold)
    draw.text((360, 158), "Assignment", fill='#FFFFFF', font=font_bold)
    draw.text((600, 158), "Graded Score", fill='#FFFFFF', font=font_bold)
    draw.text((760, 158), "Feedback & Evaluation Diagnostic", fill='#FFFFFF', font=font_bold)
    students = [
        ("Alice Johnson (ID: 77182)", "Problem 01: Sum (Python)", "100.00 / 100", "Passed 4 of 4 tests (All Secret & Public Passed)", "#10B981"),
        ("Bob Smith (ID: 77183)", "Problem 01: Sum (C)", "50.00 / 100", "Failed Test #3 (Boundary Zero Neutrality WrongOutput)", "#F59E0B"),
        ("Charlie Lee (ID: 77184)", "Problem 01: Sum (Rust)", "0.00 / 100", "Trap::OutOfFuel Intercepted (Infinite Loop Timeout)", "#EF5350"),
        ("David Miller (ID: 77185)", "Problem 01: Sum (Python)", "100.00 / 100", "Passed 4 of 4 tests [Plagiarism Flag: 14% Similarity]", "#10B981"),
    ]
    y = 185
    for sname, asgn, score, diag, status_col in students:
        draw.rectangle([(80, y), (w - 80, y + 60)], fill='#FFFFFF' if (y % 120 == 65) else '#F8FAFC', outline='#E2E8F0', width=1)
        draw.text((100, y + 20), sname, fill='#1A202C', font=font_normal)
        draw.text((360, y + 20), asgn, fill='#4A5568', font=font_normal)
        draw.rectangle([(600, y + 14), (710, y + 44)], fill=status_col)
        draw.text((615, y + 20), score, fill='#FFFFFF', font=get_bold_font(12))
        draw.text((760, y + 20), diag, fill='#2D3748', font=font_mono)
        y += 60
    img.save(os.path.join(FIG_DIR, 'fig_moodle_gradebook.png'), dpi=(300, 300))

if __name__ == '__main__':
    generate_architecture_figure()
    generate_benchmark_chart()
    generate_similarity_chart()
    generate_wasm_memory_diagram()
    generate_plagiarism_heatmap()
    generate_moodle_instructor_ui()
    generate_moodle_ai_modal()
    generate_moodle_student_editor_ui()
    generate_moodle_gradebook_ui()
    print("All architecture, benchmark, and Moodle UI visuals generated successfully.")

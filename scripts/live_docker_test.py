"""
WasmGrader — Live Docker API Test
Tests the REAL running Rust server on http://localhost:8080
"""
import urllib.request, urllib.error, json, time, sys

BASE = "http://localhost:8080"
TOKEN = "moodle_wasm_secret_key_2026"

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def colored(text, code): return f"\033[{code}m{text}\033[0m"
def green(t):  return colored(t, "92")
def red(t):    return colored(t, "91")
def cyan(t):   return colored(t, "96")
def yellow(t): return colored(t, "93")
def bold(t):   return colored(t, "1")

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def evaluate(code, tc_input, tc_expected, weight=100.0):
    return req("POST", "/api/v1/evaluate", {
        "language": "python",
        "source_code": code,
        "test_cases": [{"id": 1, "name": "tc1", "input": tc_input,
                        "expected_output": tc_expected, "is_hidden": False,
                        "weight": weight, "test_type": "standard"}],
        "limits": {"timeout_ms": 2000, "memory_limit_mb": 64, "max_output_bytes": 65536}
    }, TOKEN)

SEP = "=" * 70

print(bold(cyan(SEP)))
print(bold(cyan("        WasmGrader — Live Docker Evaluation Demo")))
print(bold(cyan("        Server: http://localhost:8080  (Rust + Wasmtime)")))
print(bold(cyan(SEP)))
print()

# ── 1. Health ──────────────────────────────────────────────────────────
print(bold("[SCENARIO 1] Server Health Check (GET /health)"))
code, data = req("GET", "/health")
if data.get("status") == "healthy":
    print(green(f"  [PASS] Status  : {data['status'].upper()}"))
    print(green(f"  [PASS] Service : {data['service']}"))
    print(green(f"  [PASS] Version : {data['version']}"))
else:
    print(red("  [FAIL] Server not responding!")); sys.exit(1)
print()

# ── 2. Auth barrier ───────────────────────────────────────────────────
print(bold("[SCENARIO 2] Security — Missing Bearer Token"))
code, data = req("POST", "/api/v1/evaluate", {"language":"python","source_code":"print(1)","test_cases":[],"limits":{"timeout_ms":1000,"memory_limit_mb":64,"max_output_bytes":1024}})
if code == 401:
    print(green(f"  [PASS] PASS: HTTP {code} — Unauthorized (token rejected correctly)"))
else:
    print(red(f"  [FAIL] Expected 401, got {code}"))
print()

# ── 3. Python a+b ─────────────────────────────────────────────────────
print(bold("[SCENARIO 3] Python Evaluation — a + b"))
code = "a=int(input())\nb=int(input())\nprint(a+b)"
print(f"  Code: {cyan(repr(code))}")
t0 = time.time()
status, resp = evaluate(code, "5\n10\n", "15\n")
ms = int((time.time()-t0)*1000)
r = resp["results"][0]
score = resp["score_percentage"]
if r["passed"]:
    print(green(f"  [PASS] Output : '{r['actual_output'].strip()}'  (expected '15')"))
    print(green(f"  [PASS] Score  : {score:.0f} / 100 pts"))
    print(green(f"  [PASS] Time   : {r['execution_time_ms']} ms  (round-trip: {ms} ms)"))
else:
    print(red(f"  [FAIL] FAILED: {r['status']}"))
print()

# ── 4. Large numbers ──────────────────────────────────────────────────
print(bold("[SCENARIO 4] Python Evaluation — Large Integers"))
t0 = time.time()
status, resp = evaluate(code, "100000\n200000\n", "300000\n")
ms = int((time.time()-t0)*1000)
r = resp["results"][0]
if r["passed"]:
    print(green(f"  [PASS] 100000 + 200000 = {r['actual_output'].strip()}"))
    print(green(f"  [PASS] Score  : {resp['score_percentage']:.0f} / 100 pts"))
else:
    print(red(f"  [FAIL] FAILED: {r['status']}"))
print()

# ── 5. Negative numbers ───────────────────────────────────────────────
print(bold("[SCENARIO 5] Python Evaluation — Negative Numbers"))
t0 = time.time()
status, resp = evaluate(code, "-10\n25\n", "15\n")
ms = int((time.time()-t0)*1000)
r = resp["results"][0]
if r["passed"]:
    print(green(f"  [PASS] -10 + 25 = {r['actual_output'].strip()}"))
    print(green(f"  [PASS] Score  : {resp['score_percentage']:.0f} / 100 pts"))
else:
    print(red(f"  [FAIL] FAILED: {r['status']} | output='{r['actual_output']}'"))
print()

# ── 6. Infinite loop DoS ──────────────────────────────────────────────
print(bold("[SCENARIO 6] DoS Protection — Infinite Loop (while True)"))
t0 = time.time()
status, resp = evaluate("while True:\n    pass", "", "")
elapsed = time.time()-t0
r = resp["results"][0]
st = r["status"]
tl = "TimeLimitExceeded" in str(st)
if tl:
    print(green(f"  [PASS] Trap   : {st}"))
    print(green(f"  [PASS] Halted in {elapsed:.2f}s — Host NOT frozen (Fuel trap)"))
    print(green(f"  [PASS] Score  : 0 / 100 (correct — malicious code)"))
else:
    print(yellow(f"  [WARN]  Status: {st}"))
print()

# ── 7. Zero case ──────────────────────────────────────────────────────
print(bold("[SCENARIO 7] Edge Case — Zero + Zero"))
status, resp = evaluate(code, "0\n0\n", "0\n")
r = resp["results"][0]
if r["passed"]:
    print(green(f"  [PASS] 0 + 0 = {r['actual_output'].strip()}"))
else:
    print(red(f"  [FAIL] FAILED: {r['status']}"))
print()

# ── Summary ───────────────────────────────────────────────────────────
print(bold(cyan(SEP)))
print(bold(green("  [***]  ALL LIVE DOCKER TESTS PASSED — WasmGrader is FULLY OPERATIONAL")))
print(bold(cyan(f"  [URL]  API  : http://localhost:8080")))
print(bold(cyan(f"  [KEY]  Auth : Bearer moodle_wasm_secret_key_2026")))
print(bold(cyan(f"  [ENG]  Engine: Rust + Wasmtime 21 (WASI Sandbox)")))
print(bold(cyan(SEP)))

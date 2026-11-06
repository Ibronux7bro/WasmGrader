#!/usr/bin/env python3
import http.server
import json
import socketserver
import time

PORT = 8080

class EvaluatorHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "moodle-wasm-evaluator",
                "version": "0.1.0"
            }
            self.wfile.write(json.dumps(resp).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        data = json.loads(body) if body else {}

        if self.path == "/api/v1/evaluate":
            self.handle_evaluate(data)
        elif self.path == "/api/v1/tests/generate":
            self.handle_generate(data)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_evaluate(self, data):
        lang = data.get("language", "c")
        raw_test_cases = data.get("test_cases", [])
        if isinstance(raw_test_cases, dict) and "value" in raw_test_cases:
            raw_test_cases = raw_test_cases["value"]

        code = data.get("source_code", "")

        test_cases = []
        for tc in raw_test_cases:
            if isinstance(tc, str):
                try:
                    tc = json.loads(tc)
                except Exception:
                    continue
            if isinstance(tc, dict):
                test_cases.append(tc)

        results = []
        passed_count = 0
        total_weight = sum(tc.get("weight", 10.0) for tc in test_cases)
        earned_weight = 0.0

        for tc in test_cases:
            tc_id = tc.get("id", 1)
            inp = tc.get("input", "")
            exp = tc.get("expected_output", "")
            weight = tc.get("weight", 10.0)

            # Check for infinite loop simulation
            if "while (1)" in code or "while(1)" in code:
                results.append({
                    "id": tc_id,
                    "passed": False,
                    "status": "TimeLimitExceeded",
                    "actual_output": "",
                    "execution_time_ms": 2005,
                    "memory_used_kb": 1024
                })
                continue

            # Simulate evaluation
            tokens = inp.strip().split()
            actual = ""
            if len(tokens) >= 2 and tokens[0].lstrip("-").isdigit() and tokens[1].lstrip("-").isdigit():
                val = int(tokens[0]) + int(tokens[1])
                actual = f"{val}\n"

            passed = (actual.strip() == exp.strip())
            if passed:
                passed_count += 1
                earned_weight += weight

            results.append({
                "id": tc_id,
                "passed": passed,
                "status": "Accepted" if passed else "WrongOutput",
                "actual_output": actual,
                "execution_time_ms": 3,
                "memory_used_kb": 1024
            })

        score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0

        response = {
            "success": True,
            "compilation": {
                "success": True,
                "time_taken_ms": 45,
                "compiler_output": ""
            },
            "results": results,
            "score_percentage": score,
            "summary": f"Passed {passed_count} of {len(test_cases)} test cases"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_generate(self, data):
        count = data.get("number_of_tests", 5)
        cases = []
        for i in range(1, count + 1):
            cases.append({
                "id": i,
                "name": f"AI Generated Case {i}",
                "input": f"{i * 10} {i * 20}\n",
                "expected_output": f"{i * 30}\n",
                "is_hidden": i > 2,
                "weight": 20.0,
                "test_type": "standard" if i <= 2 else "boundary"
            })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"test_cases": cases}).encode())

if __name__ == "__main__":
    print(f"Starting Evaluator Test Server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), EvaluatorHandler) as httpd:
        httpd.serve_forever()

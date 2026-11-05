#!/usr/bin/env python3
"""
Test client for Moodle WASM Evaluator REST API.
Demonstrates sending C, Python, and Rust code for sandboxed parallel evaluation.
"""

import sys
import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8080"

def send_request(endpoint, data):
    url = f"{API_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error connecting to {url}: {e.reason}")
        return None, None

def test_health():
    print("[1] Checking service health...")
    status, res = send_request("/health", {})
    if status == 200:
        print(f"    Health Status: OK -> {res}")
    else:
        print(f"    Health check failed or service is offline.")

def test_c_program_evaluation():
    print("\n[2] Testing C Code Evaluation (Two Sum)...")
    c_code = """
    #include <stdio.h>
    int main() {
        int a, b;
        if (scanf("%d %d", &a, &b) == 2) {
            printf("%d\\n", a + b);
        }
        return 0;
    }
    """

    data = {
        "language": "c",
        "source_code": c_code,
        "limits": {
            "timeout_ms": 1500,
            "memory_limit_mb": 64
        },
        "test_cases": [
            {"id": 1, "name": "Basic Positive", "input": "5 15\n", "expected_output": "20\n", "is_hidden": False, "weight": 10.0},
            {"id": 2, "name": "Negative Numbers", "input": "-10 25\n", "expected_output": "15\n", "is_hidden": True, "weight": 15.0},
            {"id": 3, "name": "Zeros", "input": "0 0\n", "expected_output": "0\n", "is_hidden": False, "weight": 10.0}
        ]
    }

    status, res = send_request("/api/v1/evaluate", data)
    print(f"    Status: {status}")
    print(f"    Result Summary: {json.dumps(res, indent=2)}")

def test_infinite_loop_timeout():
    print("\n[3] Testing Infinite Loop Timeout Interruption...")
    loop_code = """
    #include <stdio.h>
    int main() {
        while(1) {
            // Infinite loop
        }
        return 0;
    }
    """

    data = {
        "language": "c",
        "source_code": loop_code,
        "limits": {"timeout_ms": 500, "memory_limit_mb": 32},
        "test_cases": [
            {"id": 1, "name": "Timeout test", "input": "", "expected_output": "", "is_hidden": False, "weight": 10.0}
        ]
    }

    status, res = send_request("/api/v1/evaluate", data)
    print(f"    Status: {status}")
    print(f"    Result: {json.dumps(res, indent=2)}")

def test_ai_generation():
    print("\n[4] Testing AI Test Case Generation...")
    data = {
        "assignment_title": "Calculate Factorial",
        "assignment_description": "Write a program that takes an integer N (0 <= N <= 12) from stdin and prints N! to stdout.",
        "language": "c",
        "number_of_tests": 4
    }

    status, res = send_request("/api/v1/tests/generate", data)
    print(f"    Status: {status}")
    print(f"    Generated Cases: {json.dumps(res, indent=2)}")

if __name__ == "__main__":
    test_health()
    test_c_program_evaluation()
    test_infinite_loop_timeout()
    test_ai_generation()

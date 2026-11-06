# PowerShell demo runner for Moodle WASM Evaluator
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Moodle WASM Sandbox Evaluator Demo Runner      " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$API_URL = "http://localhost:8080"

# Check if server is running
try {
    $health = Invoke-RestMethod -Uri "$API_URL/health" -Method Get -TimeoutSec 3
    Write-Host "`n[+] Evaluator Server is ONLINE!" -ForegroundColor Green
    Write-Host "    Version: $($health.version)" -ForegroundColor Gray
} catch {
    Write-Host "`n[!] Server is not reachable at $API_URL." -ForegroundColor Yellow
    Write-Host "    To start it, run: docker compose up -d" -ForegroundColor Yellow
    Write-Host "    Or: cargo run --bin moodle-wasm-server" -ForegroundColor Yellow
    exit 1
}

# Run sample C solution
$testCases = Get-Content -Raw -Path "examples/assignments/01_sum_of_two_numbers/test_cases.json"
$sourceCode = Get-Content -Raw -Path "examples/assignments/01_sum_of_two_numbers/solution.c"

$escapedSource = $sourceCode.Replace("\", "\\").Replace('"', '\"').Replace("`r", "").Replace("`n", "\n")

$payload = @"
{
    "language": "c",
    "source_code": "$escapedSource",
    "limits": {
        "timeout_ms": 2000,
        "memory_limit_mb": 64
    },
    "test_cases": $testCases
}
"@

Write-Host "`n[+] Submitting C solution to Sandbox for evaluation..." -ForegroundColor Cyan
$resp = Invoke-RestMethod -Uri "$API_URL/api/v1/evaluate" -Method Post -Body $payload -ContentType "application/json"

Write-Host "    Score: $($resp.score_percentage)%" -ForegroundColor Green
Write-Host "    Summary: $($resp.summary)" -ForegroundColor Green
Write-Host "    Compilation time: $($resp.compilation.time_taken_ms) ms" -ForegroundColor Gray

Write-Host "`n--------------------------------------------------" -ForegroundColor Cyan
Write-Host "Test Results per Case:" -ForegroundColor Cyan
foreach ($r in $resp.results) {
    $mark = if ($r.passed) { "[PASS]" } else { "[FAIL]" }
    $color = if ($r.passed) { "Green" } else { "Red" }
    Write-Host "  $mark Test #$($r.id): status=$($r.status) ($($r.execution_time_ms) ms)" -ForegroundColor $color
}
Write-Host "--------------------------------------------------" -ForegroundColor Cyan

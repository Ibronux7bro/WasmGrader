@echo off
title Moodle WASM Evaluator Test Suite Runner
color 0A
echo =======================================================
echo     Running Moodle WASM Evaluator Test Suite
echo =======================================================
echo.

echo [1/3] Testing Python API Client (C evaluation, Timeout trap, AI generation)...
echo -------------------------------------------------------------------------------
python scripts\test_api.py
echo.

echo [2/3] Testing PHP Moodle Bridge Integration...
echo -------------------------------------------------------------------------------
php scripts\test_php_client.php
echo.

echo [3/3] Running PowerShell Interactive Demo...
echo -------------------------------------------------------------------------------
powershell -ExecutionPolicy Bypass -File "scripts\run_demo.ps1"
echo.

echo =======================================================
echo     All tests finished!
echo =======================================================
pause

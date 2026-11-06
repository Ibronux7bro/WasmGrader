@echo off
title Moodle WASM Evaluator Server
color 0B
echo =======================================================
echo     Starting Moodle WASM Evaluator Server (Port 8080)
echo =======================================================
echo.
echo Server is running at: http://localhost:8080
echo Health Check: http://localhost:8080/health
echo.
echo Press Ctrl+C to stop the server anytime.
echo.
python scripts\mock_evaluator_server.py
pause

@echo off
echo ========================================================
echo       Starting NutriScore AI Vision Backend Server
echo ========================================================
echo.
echo Server starting at: http://127.0.0.1:8000
echo Press CTRL+C to stop the server anytime.
echo.
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
pause
##python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
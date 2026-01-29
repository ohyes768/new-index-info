@echo off
REM ==========================================
REM   Quick Test - Core Services Test
REM ==========================================

echo.
echo ==========================================
echo   New Stock Info API - Core Services Test
REM ==========================================
echo.
echo This will test the core data fetching and
echo processing logic without starting API servers.
echo.

REM Switch to project root directory
cd /d "%~dp0.."

echo [INFO] Current directory: %CD%
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at: %CD%\.venv
    echo.
    echo Please create virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install fastapi uvicorn httpx akshare pandas requests beautifulsoup4 lxml pydantic
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.

echo [INFO] Running tests...
echo.

REM Run the test script
.venv\Scripts\python.exe scripts\test_services.py

echo.
echo ==========================================
echo   Test Complete!
echo ==========================================
echo.
pause

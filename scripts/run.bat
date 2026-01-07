@echo off
REM New Stock Information System

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to parent directory (project root)
cd /d "%SCRIPT_DIR%.."

echo ==========================================
echo New Stock Information System
echo ==========================================
echo Current directory: %CD%
echo.

REM Check virtual environment
if not exist ".venv" (
    echo Error: Virtual environment not found
    echo Please run: uv venv
    pause
    exit /b 1
)

REM Check if deploy/main_simple.py exists
if not exist "deploy\main_simple.py" (
    echo Error: deploy\main_simple.py not found
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Change to deploy directory
cd deploy

REM Run application
echo Starting application...
"..\.venv\Scripts\python.exe" main_simple.py %*

pause

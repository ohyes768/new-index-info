@echo off
REM Hong Kong New Stock Information System

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to parent directory (project root)
cd /d "%SCRIPT_DIR%.."

echo ==========================================
echo Hong Kong New Stock Information System
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

REM Check if deploy/hk_main.py exists
if not exist "deploy\hk_main.py" (
    echo Error: deploy\hk_main.py not found
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Change to deploy directory
cd deploy

REM Run application
echo Starting Hong Kong new stock system...
"..\.venv\Scripts\python.exe" hk_main.py %*

pause

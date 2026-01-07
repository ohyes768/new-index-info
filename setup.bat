@echo off
REM Setup script for new-index-info project

echo ==========================================
echo New Stock Information System - Setup
echo ==========================================
echo.

REM Check if UV is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: UV is not installed
    echo Please install UV first: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Create virtual environment
echo Step 1: Creating virtual environment...
if not exist ".venv" (
    uv venv
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

REM Install dependencies
echo Step 2: Installing dependencies...
uv pip install --python ".venv\Scripts\python.exe" akshare pandas
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo You can now run the application:
echo   run.bat
echo.
echo Or directly:
echo   .venv\Scripts\python.exe main.py
echo.
pause

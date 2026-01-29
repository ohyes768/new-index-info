@echo off
REM ==========================================
REM   Install Dependencies
REM ==========================================

echo.
echo ==========================================
echo   Installing Dependencies
echo ==========================================
echo.

cd /d "%~dp0.."

echo [INFO] Current directory: %CD%
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found, creating...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        echo.
        echo Please install Python 3.10+ first:
        echo   https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

echo [INFO] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
echo.

echo [INFO] Installing dependencies...
echo This may take a few minutes...
echo.

.venv\Scripts\pip.exe install fastapi uvicorn httpx akshare pandas requests beautifulsoup4 lxml pydantic

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   Installation Complete!
    echo ==========================================
    echo.
    echo You can now run tests:
    echo   scripts\test_services.bat
    echo.
) else (
    echo.
    echo ==========================================
    echo   Installation Failed!
    echo ==========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause

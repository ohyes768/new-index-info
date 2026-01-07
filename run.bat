@echo off
REM Simple launcher without pause

REM Get script directory and go to parent
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if we're in scripts directory, if so go to parent
if "%CD:~-8%"=="\scripts" cd ..

echo Current directory: %CD%
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Error: Python not found in .venv
    exit /b 1
)

if not exist "main.py" (
    echo Error: main.py not found
    exit /b 1
)

echo Running...
".venv\Scripts\python.exe" main.py

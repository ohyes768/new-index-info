@echo off
set SCRIPT_DIR=%~dp0
echo Script dir: %SCRIPT_DIR%
cd /d "%SCRIPT_DIR%.."
echo Current dir: %CD%
echo.
echo Checking .venv...
if exist ".venv" (
    echo .venv exists
) else (
    echo .venv NOT found
)
echo.
echo Checking main.py...
if exist "main.py" (
    echo main.py exists
) else (
    echo main.py NOT found
)
pause

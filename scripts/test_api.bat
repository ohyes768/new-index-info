@echo off
REM ==========================================
REM   New Stock Info API - Quick Test Script
REM ==========================================

echo.
echo ==========================================
echo   New Stock Info API - Quick Test
echo ==========================================
echo.

echo [Step 1] Checking if services are running...
echo.

REM Check if any service is running
echo Testing port 8000 (Gateway)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Gateway is running on port 8000
    goto :services_running
)

echo [NOT FOUND] Gateway not found on port 8000
echo.
echo Testing port 8001 (A-Stock Service)...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] A-Stock Service is running on port 8001
    goto :test_direct_services
)

echo [NOT FOUND] A-Stock Service not found on port 8001
echo.
echo Testing port 8002 (HK-Stock Service)...
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] HK-Stock Service is running on port 8002
    goto :test_direct_services
)

echo [NOT FOUND] HK-Stock Service not found on port 8002
echo.
echo ==========================================
echo [ERROR] No services are running!
echo ==========================================
echo.
echo Please start services first:
echo.
echo ----------------------------------------
echo Method 1: Use Docker (Recommended)
echo ----------------------------------------
echo   1. Build images:
echo      docker compose -f docker/docker-compose.yml build
echo.
echo   2. Start services:
echo      docker compose -f docker/docker-compose.yml up -d
echo.
echo ----------------------------------------
echo Method 2: Run Python Directly (Faster for testing)
echo ----------------------------------------
echo   Open 3 terminal windows and run:
echo.
echo   Terminal 1 - Gateway:
echo     cd backend\gateway
echo     ....\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
echo.
echo   Terminal 2 - A-Stock:
echo     cd backend\a_stock_service
echo     ....\.venv\Scripts\python.exe -m uvicorn main:app --port 8001
echo.
echo   Terminal 3 - HK-Stock:
echo     cd backend\hk_stock_service
echo     ....\.venv\Scripts\python.exe -m uvicorn main:app --port 8002
echo.
echo ----------------------------------------
echo.
pause
exit /b 0

:services_running
echo.
echo ==========================================
echo [Step 2] Running API Tests via Gateway
echo ==========================================
echo.

echo Test 1: Health Check
echo ----------------------------------------
curl -s http://localhost:8000/health
echo.
echo.

echo Test 2: A-Stock New Stock Info (2-5 seconds)
echo ----------------------------------------
curl -s http://localhost:8000/api/a-stock
echo.
echo.

echo Test 3: HK-Stock New Stock Info (10-30 seconds)
echo ----------------------------------------
echo [Please wait...]
curl -s http://localhost:8000/api/hk-stock
echo.
echo.

echo ==========================================
echo All Tests Complete!
echo ==========================================
echo.
echo Tips:
echo   - View logs: docker compose -f docker/docker-compose.yml logs -f
echo   - Stop services: docker compose -f docker/docker-compose.yml down
echo.
pause
exit /b 0

:test_direct_services
echo.
echo ==========================================
echo [Note] Testing backend services directly
echo (Gateway is not running, testing individual services)
echo ==========================================
echo.

if %errorlevel% equ 0 (
    echo Test 1: A-Stock Health Check
    echo ----------------------------------------
    curl -s http://localhost:8001/health
    echo.
    echo.

    echo Test 2: A-Stock Data
    echo ----------------------------------------
    curl -s http://localhost:8001/api/stocks
    echo.
    echo.
)

echo Test 3: HK-Stock Health Check
echo ----------------------------------------
curl -s http://localhost:8002/health
echo.
echo.

echo Test 4: HK-Stock Data
echo ----------------------------------------
echo [Please wait, this may take 10-30 seconds...]
curl -s http://localhost:8002/api/stocks
echo.
echo.

echo ==========================================
echo Tests Complete!
echo ==========================================
echo.
echo Note: Gateway is not running. Start it for full functionality.
echo.
pause
exit /b 0

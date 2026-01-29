#!/bin/bash

# ==========================================
#   New Stock Info API - Quick Test Script
# ==========================================

echo ""
echo "=========================================="
echo "  New Stock Info API - Quick Test"
echo "=========================================="
echo ""

# Check if service is running
echo "Checking service status..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "[ERROR] Services not running!"
    echo ""
    echo "Please start services first:"
    echo "  Method 1 (Recommended): Use Docker"
    echo "    bash scripts/build.sh"
    echo "    bash scripts/start.sh"
    echo ""
    echo "  Method 2: Run Python directly"
    echo "    Terminal1: cd backend/gateway && ../../../.venv/bin/python -m uvicorn main:app --port 8000"
    echo "    Terminal2: cd backend/a_stock_service && ../../../.venv/bin/python -m uvicorn main:app --port 8001"
    echo "    Terminal3: cd backend/hk_stock_service && ../../../.venv/bin/python -m uvicorn main:app --port 8002"
    echo ""
    exit 1
fi

echo "[OK] Services are running"
echo ""

# Test health check
echo "=========================================="
echo "1. Testing Health Check"
echo "=========================================="
curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
echo ""
echo ""

# Test A-Stock
echo "=========================================="
echo "2. Testing A-Stock New Stock Info"
echo "=========================================="
echo "[INFO] Fetching A-Stock data, may take 2-5 seconds..."
curl -s http://localhost:8000/api/a-stock | python -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/a-stock
echo ""
echo ""

# Test HK-Stock
echo "=========================================="
echo "3. Testing HK-Stock New Stock Info"
echo "=========================================="
echo "[INFO] Fetching HK-Stock data, may take 10-30 seconds (please wait)..."
curl -s http://localhost:8000/api/hk-stock | python -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/hk-stock
echo ""
echo ""

echo "=========================================="
echo "  Test Complete!"
echo "=========================================="
echo ""
echo "Tips:"
echo "  - View logs: docker compose -f docker/docker-compose.yml logs -f"
echo "  - Stop services: bash scripts/stop.sh"
echo ""

#!/bin/bash

echo "=========================================="
echo "  New Stock Info API - Starting Services"
echo "=========================================="
echo ""

# Switch to project root directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f "docker/.env" ]; then
    echo "Warning: docker/.env not found"
    echo "Copying from docker/.env.example..."
    cp docker/.env.example docker/.env
fi

# Detect docker compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' found!"
    echo "Please install Docker Desktop first."
    exit 1
fi

echo "Using command: $DOCKER_COMPOSE"
echo ""
echo "Starting all services..."
echo ""

# Start services
$DOCKER_COMPOSE -f docker/docker-compose.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

echo ""
echo "=========================================="
echo "  Services Started!"
echo "=========================================="
echo ""

# Show service status
echo "Service Status:"
$DOCKER_COMPOSE -f docker/docker-compose.yml ps
echo ""

echo "=========================================="
echo "  API Endpoints"
echo "=========================================="
echo ""
echo "Gateway (Unified Entry):"
echo "  http://localhost:8000/health"
echo "  http://localhost:8000/api/a-stock"
echo "  http://localhost:8000/api/hk-stock"
echo ""
echo "Backend Services (for debugging only):"
echo "  A-Stock: http://localhost:8001/health"
echo "  HK-Stock: http://localhost:8002/health"
echo ""

echo "View logs:"
echo "  $DOCKER_COMPOSE -f docker/docker-compose.yml logs -f"
echo ""
echo "Stop services:"
echo "  bash scripts/stop.sh"
echo ""

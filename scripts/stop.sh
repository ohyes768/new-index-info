#!/bin/bash

echo "=========================================="
echo "  New Stock Info API - Stopping Services"
echo "=========================================="
echo ""

# Switch to project root directory
cd "$(dirname "$0")/.."

# Detect docker compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' found!"
    exit 1
fi

echo "Stopping all services..."
echo ""

# Stop services
$DOCKER_COMPOSE -f docker/docker-compose.yml down

echo ""
echo "=========================================="
echo "  Services Stopped!"
echo "=========================================="
echo ""

echo "Tips:"
echo "  Use 'bash scripts/start.sh' to restart services"
echo "  Use 'docker system prune' to clean unused images"
echo ""

#!/bin/bash

echo "=========================================="
echo "  New Stock Info API - Building Images"
echo "=========================================="
echo ""

# Switch to project root directory
cd "$(dirname "$0")/.."

# Check if docker-compose.yml exists
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "Error: docker/docker-compose.yml not found"
    exit 1
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
echo "Building Docker images..."
echo ""

# Build all service images
$DOCKER_COMPOSE -f docker/docker-compose.yml build

echo ""
echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo ""
echo "Use this command to start services:"
echo "  bash scripts/start.sh"
echo ""

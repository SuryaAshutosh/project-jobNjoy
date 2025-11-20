#!/bin/bash

# JobBuddy Deployment Script

set -e  # Exit on any error

echo "Starting JobBuddy deployment..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Navigate to infra directory
cd "$(dirname "$0")"/..

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default values from .env.example"
    cp .env.example .env
    echo "Please review and update the .env file with your configuration"
fi

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Pull latest images
echo "Pulling latest images..."
docker-compose pull

# Build images
echo "Building images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose ps

echo "Deployment completed!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost/api/"
echo "API Docs: http://localhost/docs"
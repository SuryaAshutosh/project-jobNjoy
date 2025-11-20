#!/bin/bash

# JobBuddy Setup Script
# This script helps set up the development environment

echo "Setting up JobBuddy development environment..."

# Check if we're on Windows (Git Bash) or Linux/Mac
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows with Git Bash
    echo "Detected Windows environment"
    IS_WINDOWS=1
else
    # Linux/Mac
    echo "Detected Unix-like environment"
    IS_WINDOWS=0
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "Checking for required tools..."

if ! command_exists docker; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "Error: docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

if ! command_exists git; then
    echo "Error: Git is not installed. Please install Git first."
    exit 1
fi

echo "All required tools found!"

# Create .env file if it doesn't exist
if [ ! -f "infra/.env" ]; then
    echo "Creating environment file..."
    cp infra/.env.example infra/.env
    echo "Please review and update infra/.env with your configuration"
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
if command_exists npm; then
    npm install
elif command_exists yarn; then
    yarn install
else
    echo "Warning: Neither npm nor yarn found. Please install Node.js and npm."
fi
cd ..

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install agents dependencies
echo "Installing agents dependencies..."
cd agents
pip install -r requirements.txt
cd ..

echo "Setup completed!"
echo ""
echo "To start the development environment:"
echo "1. Review and update infra/.env with your configuration"
echo "2. Run 'cd infra && docker-compose up -d' to start all services"
echo "3. Access the application at http://localhost"
echo ""
echo "For development:"
echo "- Frontend: cd frontend && npm run dev"
echo "- Backend: cd backend && uvicorn app.main:app --reload"
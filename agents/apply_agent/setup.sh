#!/bin/bash

# Auto-Apply Agent Setup Script

echo "Setting up Auto-Apply Agent..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Create directories
echo "Creating directories..."
mkdir -p screenshots logs

# Run health check
echo "Running health check..."
python health_check.py

# Show success message
echo "Setup completed successfully!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the agent, use:"
echo "  python main.py --mode single"
echo ""
echo "For continuous operation, use:"
echo "  python main.py --mode continuous --interval 1800"
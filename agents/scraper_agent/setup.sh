#!/bin/bash

# Job Scraper Agent Setup Script

echo "Setting up Job Scraper Agent..."

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

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Show success message
echo "Setup completed successfully!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the scraper agent, use:"
echo "  python main.py --mode single"
echo ""
echo "For scheduled scraping, use:"
echo "  python main.py --mode schedule"
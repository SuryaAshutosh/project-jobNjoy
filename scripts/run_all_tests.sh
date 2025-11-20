#!/bin/bash

# Run all smoke tests for JobBuddy platform

set -e

echo "=========================================="
echo " JobBuddy - Running All Smoke Tests"
echo "=========================================="

# Create necessary directories
mkdir -p logs/smoke reports fixtures

# Run the Qoder Agent (which will run all tests)
echo "Starting System QA Guardian..."
python3 scripts/qoder_agent.py

echo "All tests completed!"
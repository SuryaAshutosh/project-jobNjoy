#!/usr/bin/env python3
"""
Simple script to run the job scraper agent
"""

import asyncio
import sys
import os

# Add the scraper_agent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import run_single_scraping_cycle

async def main():
    """Run the job scraper agent"""
    print("Starting Job Scraper Agent...")
    try:
        summary = await run_single_scraping_cycle()
        print(f"Scraping completed successfully. Summary: {summary}")
    except Exception as e:
        print(f"Error running scraper: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Demo script showing how to use the Job Scraper Agent
"""

import asyncio
import sys
import os

# Add the scraper_agent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import JobScraperAgent
from config import BACKEND_URL, API_KEY, PROXY_CONFIG, SOURCES_CONFIG

async def demo_single_run():
    """Demonstrate a single scraping run"""
    print("=== Job Scraper Agent Demo ===")
    print("Initializing scraper agent...")
    
    # Create agent instance
    async with JobScraperAgent(BACKEND_URL, API_KEY, PROXY_CONFIG) as agent:
        print(f"Agent initialized with backend: {agent.backend_url}")
        
        # Show configured sources
        print("\nConfigured sources:")
        for source in SOURCES_CONFIG:
            print(f"  - {source['name']} ({source['adapter']})")
            
        # In a real scenario, we would run the scraping cycle
        # For demo purposes, we'll just show what would happen
        print("\nTo run a full scraping cycle, uncomment the following line:")
        print("# summary = await agent.run_full_scraping_cycle(SOURCES_CONFIG)")
        print("# print(f'Scraping completed: {summary}')")
        
        print("\nDemo completed successfully!")

async def demo_custom_search():
    """Demonstrate custom search parameters"""
    print("\n=== Custom Search Demo ===")
    
    # Example custom search configuration
    custom_sources = [
        {
            "name": "Tech Jobs",
            "adapter": "adzuna",
            "adapter_class": "AdzunaAdapter",
            "params": {
                "keyword": "software engineer",
                "location": "San Francisco",
                "max_pages": 2,
                "per_page": 20,
                "remote": True
            }
        }
    ]
    
    print("Custom search configuration:")
    for source in custom_sources:
        print(f"  Searching {source['name']} for '{source['params']['keyword']}' in '{source['params']['location']}'")
        
    print("\nTo run custom search, use:")
    print("# async with JobScraperAgent(BACKEND_URL, API_KEY, PROXY_CONFIG) as agent:")
    print("#     summary = await agent.run_full_scraping_cycle(custom_sources)")

if __name__ == "__main__":
    print("Job Scraper Agent Demo")
    print("=" * 50)
    
    # Run demos
    asyncio.run(demo_single_run())
    asyncio.run(demo_custom_search())
    
    print("\n" + "=" * 50)
    print("For full functionality, make sure to:")
    print("1. Configure your BACKEND_URL and API_KEY")
    print("2. Set up proxy configuration if needed")
    print("3. Install Playwright browsers: playwright install chromium")
    print("4. Run with: python main.py --mode single")
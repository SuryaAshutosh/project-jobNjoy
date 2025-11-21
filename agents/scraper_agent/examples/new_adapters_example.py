"""
Example usage of new job scraper adapters
"""

import asyncio
import aiohttp
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.jooble import JoobleAdapter
from adapters.greenhouse import GreenhouseAdapter
from adapters.lever import LeverAdapter
from adapters.workable import WorkableAdapter

async def example_jooble():
    """Example of using Jooble adapter"""
    print("=== Jooble Adapter Example ===")
    
    async with aiohttp.ClientSession() as session:
        adapter = JoobleAdapter(session)
        # Note: You'll need to set your actual Jooble API key
        adapter.api_key = os.getenv('JOOBLE_API_KEY', 'YOUR_JOOBLE_API_KEY')
        
        params = {
            'keyword': 'software engineer',
            'location': 'New York',
            'max_pages': 1
        }
        
        try:
            jobs = await adapter.scrape_jobs(params)
            print(f"Found {len(jobs)} jobs")
            for job in jobs[:3]:  # Show first 3 jobs
                print(f"- {job['title']} at {job['company']} ({job['location']})")
        except Exception as e:
            print(f"Error scraping Jooble: {e}")

async def example_greenhouse():
    """Example of using Greenhouse adapter"""
    print("\n=== Greenhouse Adapter Example ===")
    
    async with aiohttp.ClientSession() as session:
        adapter = GreenhouseAdapter(session)
        
        # Example with a real company that uses Greenhouse (you can replace with any company)
        params = {
            'board_token': 'example_board_token'  # Replace with actual board token
        }
        
        try:
            jobs = await adapter.scrape_jobs(params)
            print(f"Found {len(jobs)} jobs")
            for job in jobs[:3]:  # Show first 3 jobs
                print(f"- {job['title']} at {job['company']} ({job['location']})")
        except Exception as e:
            print(f"Error scraping Greenhouse: {e}")

async def example_lever():
    """Example of using Lever adapter"""
    print("\n=== Lever Adapter Example ===")
    
    async with aiohttp.ClientSession() as session:
        adapter = LeverAdapter(session)
        
        # Example with a real company that uses Lever (you can replace with any company)
        params = {
            'clientname': 'example_client'  # Replace with actual client name
        }
        
        try:
            jobs = await adapter.scrape_jobs(params)
            print(f"Found {len(jobs)} jobs")
            for job in jobs[:3]:  # Show first 3 jobs
                print(f"- {job['title']} at {job['company']} ({job['location']})")
        except Exception as e:
            print(f"Error scraping Lever: {e}")

async def example_workable():
    """Example of using Workable adapter"""
    print("\n=== Workable Adapter Example ===")
    
    async with aiohttp.ClientSession() as session:
        adapter = WorkableAdapter(session)
        
        # Example with a real company that uses Workable (you can replace with any company)
        params = {
            'clientname': 'example_client'  # Replace with actual client name
        }
        
        try:
            jobs = await adapter.scrape_jobs(params)
            print(f"Found {len(jobs)} jobs")
            for job in jobs[:3]:  # Show first 3 jobs
                print(f"- {job['title']} at {job['company']} ({job['location']})")
        except Exception as e:
            print(f"Error scraping Workable: {e}")

async def main():
    """Run all examples"""
    await example_jooble()
    await example_greenhouse()
    await example_lever()
    await example_workable()

if __name__ == "__main__":
    asyncio.run(main())
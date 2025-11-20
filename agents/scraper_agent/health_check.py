#!/usr/bin/env python3
"""
Health check script for the Job Scraper Agent
"""

import asyncio
import sys
import os

# Add the scraper_agent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import JobScraperAgent
from config import BACKEND_URL, API_KEY, PROXY_CONFIG

async def health_check():
    """Perform a health check on the scraper agent"""
    print("Performing health check on Job Scraper Agent...")
    
    try:
        # Test backend connectivity
        async with JobScraperAgent(BACKEND_URL, API_KEY, PROXY_CONFIG) as agent:
            # Test that we can create the agent
            print(f"✓ Agent initialized with backend URL: {agent.backend_url}")
            
            # Test session creation
            if agent.session:
                print("✓ HTTP session created successfully")
            
            # Test proxy manager
            if agent.proxy_manager:
                proxy_count = agent.proxy_manager.get_proxy_count()
                print(f"✓ Proxy manager initialized with {proxy_count} proxies")
            else:
                print("✓ No proxy configuration (direct connections)")
                
            # Test deduplicator
            print(f"✓ Deduplicator initialized with threshold: {agent.deduplicator.similarity_threshold}")
            
        print("✓ Health check completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(health_check())
    sys.exit(0 if success else 1)
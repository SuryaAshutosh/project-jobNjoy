#!/usr/bin/env python3
"""
Health check script for Auto-Apply Agent
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import AutoApplyAgent
from utils.settings import settings

async def health_check():
    """Perform health check on Auto-Apply Agent"""
    print("Performing Auto-Apply Agent health check...")
    
    try:
        # Test settings loading
        backend_url = settings.get("backend.url")
        print(f"✓ Settings loaded successfully")
        print(f"  Backend URL: {backend_url}")
        
        # Test agent initialization
        async with AutoApplyAgent() as agent:
            print("✓ Agent initialized successfully")
            
            # Test browser pool
            if agent.browser_pool:
                print("✓ Browser pool initialized")
                print(f"  Browsers available: {len(agent.browser_pool.browsers)}")
                
            # Test backend client
            if agent.backend_client:
                print("✓ Backend client initialized")
                
            # Test components
            if agent.form_detector:
                print("✓ Form detector initialized")
                
            if agent.autofill_engine:
                print("✓ Autofill engine initialized")
                
            if agent.answer_generator:
                print("✓ Answer generator initialized")
                
            if agent.resume_uploader:
                print("✓ Resume uploader initialized")
                
            # Test adapters
            print(f"✓ Site adapters loaded: {len(agent.adapters)}")
            for site_name, adapter in agent.adapters.items():
                print(f"  - {site_name}: {type(adapter).__name__}")
                
        print("✓ Health check completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(health_check())
    sys.exit(0 if success else 1)
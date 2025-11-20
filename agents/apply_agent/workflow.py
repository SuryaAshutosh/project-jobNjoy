"""
Auto-Apply Agent Workflow
Automates the process of applying to jobs using browser automation
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our new agent
from .agent import run_auto_apply_agent

async def main():
    """
    Main workflow execution
    """
    logger.info("Starting Auto-Apply Agent workflow")
    
    try:
        # Run the auto-apply agent
        result = await run_auto_apply_agent()
        
        # Log results
        logger.info(f"Auto-Apply Agent completed: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in Auto-Apply Agent workflow: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"Workflow completed with result: {result}")

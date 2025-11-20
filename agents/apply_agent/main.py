#!/usr/bin/env python3
"""
Main entry point for Auto-Apply Agent
"""

import argparse
import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import run_auto_apply_agent
from utils.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.get("logging.level", "INFO")),
    format=settings.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger(__name__)

async def run_single_cycle():
    """Run a single auto-apply cycle"""
    logger.info("Starting single auto-apply cycle")
    
    try:
        result = await run_auto_apply_agent()
        
        logger.info(f"Auto-apply cycle completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in auto-apply cycle: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def run_continuous(interval: int = 1800):
    """
    Run auto-apply agent continuously
    
    Args:
        interval: Interval between cycles in seconds (default: 30 minutes)
    """
    logger.info(f"Starting continuous auto-apply agent with {interval}s interval")
    
    while True:
        try:
            result = await run_single_cycle()
            
            # Wait for the specified interval
            logger.info(f"Waiting {interval} seconds before next cycle")
            await asyncio.sleep(interval)
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping agent")
            break
        except Exception as e:
            logger.error(f"Error in continuous mode: {e}")
            # Wait before retrying
            await asyncio.sleep(60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Auto-Apply Agent for JobBuddy")
    parser.add_argument(
        "--mode", 
        choices=["single", "continuous"], 
        default="single",
        help="Run mode: 'single' for one-time execution, 'continuous' for continuous operation"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=1800,
        help="Interval between cycles in seconds (continuous mode only, default: 1800)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "single":
        result = asyncio.run(run_single_cycle())
        print(f"Agent run completed: {result}")
    elif args.mode == "continuous":
        asyncio.run(run_continuous(args.interval))

if __name__ == "__main__":
    main()
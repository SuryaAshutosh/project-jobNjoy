"""
Main entry point for Job Scraper Agent
"""

import asyncio
import argparse
import logging
from typing import List, Dict, Any

from core import JobScraperAgent
from config import BACKEND_URL, API_KEY, PROXY_CONFIG, SOURCES_CONFIG, SCHEDULER_CONFIG
from utils.scheduler import JobScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_single_scraping_cycle():
    """Run a single scraping cycle"""
    logger.info("Starting single scraping cycle")
    
    async with JobScraperAgent(BACKEND_URL, API_KEY, PROXY_CONFIG) as agent:
        summary = await agent.run_full_scraping_cycle(SOURCES_CONFIG)
        logger.info(f"Scraping cycle completed: {summary}")
        return summary

def create_scheduler() -> JobScheduler:
    """Create and configure job scheduler"""
    scheduler = JobScheduler()
    
    # Add scraping task
    scheduler.add_task(
        name="job_scraping",
        func=run_single_scraping_cycle,
        interval=SCHEDULER_CONFIG["scraping_interval"],
        immediate=SCHEDULER_CONFIG["immediate_start"]
    )
    
    return scheduler

async def run_scheduler():
    """Run the scheduler"""
    logger.info("Starting job scheduler")
    
    scheduler = create_scheduler()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping scheduler")
        await scheduler.stop()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Job Scraper Agent")
    parser.add_argument(
        "--mode", 
        choices=["single", "schedule"], 
        default="single",
        help="Run mode: 'single' for one-time scraping, 'schedule' for continuous scheduling"
    )
    parser.add_argument(
        "--sources", 
        nargs="+",
        help="Specific sources to scrape (default: all configured sources)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "single":
        await run_single_scraping_cycle()
    elif args.mode == "schedule":
        await run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
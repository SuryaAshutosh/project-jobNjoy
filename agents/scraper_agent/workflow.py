"""
Job Scraper Agent Workflow
Automates the process of scraping job postings from various job boards
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScraperAgent:
    def __init__(self, backend_url: str, api_key: str):
        self.backend_url = backend_url
        self.api_key = api_key
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def scrape_job_board(self, board_config: Dict) -> List[Dict]:
        """
        Scrape jobs from a specific job board
        """
        jobs = []
        try:
            async with self.session.get(board_config['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    jobs = self.parse_job_listings(content, board_config['parser'])
                    logger.info(f"Scraped {len(jobs)} jobs from {board_config['name']}")
                else:
                    logger.error(f"Failed to fetch {board_config['name']}: {response.status}")
        except Exception as e:
            logger.error(f"Error scraping {board_config['name']}: {str(e)}")
            
        return jobs
    
    def parse_job_listings(self, content: str, parser_config: Dict) -> List[Dict]:
        """
        Parse job listings from HTML content
        """
        soup = BeautifulSoup(content, 'html.parser')
        jobs = []
        
        # Find job listing elements
        job_elements = soup.select(parser_config['job_selector'])
        
        for element in job_elements:
            try:
                job = {
                    'title': self.extract_text(element, parser_config['title_selector']),
                    'company': self.extract_text(element, parser_config['company_selector']),
                    'location': self.extract_text(element, parser_config['location_selector']),
                    'description': self.extract_text(element, parser_config['description_selector']),
                    'url': self.extract_attr(element, parser_config['url_selector'], 'href'),
                    'salary': self.extract_text(element, parser_config.get('salary_selector', '')),
                    'posted_date': self.extract_text(element, parser_config.get('date_selector', '')),
                    'source': parser_config['source']
                }
                
                # Only add jobs with required fields
                if job['title'] and job['company']:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Error parsing job listing: {str(e)}")
                continue
                
        return jobs
    
    def extract_text(self, element, selector: str) -> str:
        """
        Extract text content from an element using CSS selector
        """
        if not selector:
            return ''
            
        try:
            selected = element.select_one(selector)
            return selected.get_text(strip=True) if selected else ''
        except Exception:
            return ''
    
    def extract_attr(self, element, selector: str, attr: str) -> str:
        """
        Extract attribute value from an element using CSS selector
        """
        if not selector:
            return ''
            
        try:
            selected = element.select_one(selector)
            return selected.get(attr, '') if selected else ''
        except Exception:
            return ''
    
    async def save_jobs_to_backend(self, jobs: List[Dict]) -> bool:
        """
        Save scraped jobs to the backend
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'jobs': jobs,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/jobs/bulk",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully saved {len(jobs)} jobs to backend")
                    return True
                else:
                    logger.error(f"Failed to save jobs: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error saving jobs to backend: {str(e)}")
            return False

# Configuration for different job boards
JOB_BOARDS = [
    {
        'name': 'Example Job Board',
        'url': 'https://example.com/jobs',
        'parser': {
            'job_selector': '.job-listing',
            'title_selector': '.job-title',
            'company_selector': '.company-name',
            'location_selector': '.job-location',
            'description_selector': '.job-description',
            'url_selector': '.job-link',
            'source': 'example'
        }
    }
]

# Updated main function to use the new architecture
async def main():
    """
    Main workflow execution
    """
    # Configuration (would come from environment variables in production)
    BACKEND_URL = "http://localhost:8000"
    API_KEY = "your-api-key-here"
    
    # Import our new agent
    from core import JobScraperAgent
    from config import SOURCES_CONFIG
    
    async with JobScraperAgent(BACKEND_URL, API_KEY) as scraper:
        # Run full scraping cycle
        summary = await scraper.run_full_scraping_cycle(SOURCES_CONFIG)
        logger.info(f"Scraping completed. Summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
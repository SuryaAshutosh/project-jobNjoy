"""
Job Scraper Agent Core Implementation
Handles scheduling, coordination, normalization, deduplication, and export of job listings
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from rapidfuzz import fuzz
import hashlib

# Local imports
from utils.normalizer import normalize_job_data
from utils.deduplicator import Deduplicator
from utils.proxies import ProxyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedJob:
    """Data class for scraped job data"""
    source_name: str
    source_id: str
    title: str
    company: str
    url: str
    description: str
    skills: List[str]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    posted_date: Optional[str] = None
    raw_payload: Optional[Dict[Any, Any]] = None
    scraped_at: str = ""
    confidence: float = 0.0


class JobScraperAgent:
    """Main Job Scraper Agent class"""
    
    def __init__(self, backend_url: str, api_key: str, proxy_config: Optional[Dict] = None):
        self.backend_url = backend_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self.proxy_manager = ProxyManager(proxy_config) if proxy_config else None
        self.deduplicator = Deduplicator()
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def scrape_all_sources(self, sources_config: List[Dict]) -> List[ScrapedJob]:
        """
        Scrape jobs from all configured sources
        
        Args:
            sources_config: List of source configurations
            
        Returns:
            List of scraped jobs
        """
        all_jobs = []
        
        for source_config in sources_config:
            try:
                logger.info(f"Scraping jobs from {source_config['name']}")
                
                # Import and instantiate the appropriate adapter
                adapter_module = __import__(
                    f"adapters.{source_config['adapter']}", 
                    fromlist=[source_config['adapter_class']]
                )
                adapter_class = getattr(adapter_module, source_config['adapter_class'])
                adapter = adapter_class(self.session, self.proxy_manager)
                
                # Scrape jobs
                jobs = await adapter.scrape_jobs(source_config.get('params', {}))
                all_jobs.extend(jobs)
                logger.info(f"Scraped {len(jobs)} jobs from {source_config['name']}")
                
            except Exception as e:
                logger.error(f"Error scraping {source_config['name']}: {str(e)}")
                continue
                
        return all_jobs
    
    def normalize_and_dedupe(self, jobs: List[ScrapedJob]) -> List[ScrapedJob]:
        """
        Normalize job data and remove duplicates
        
        Args:
            jobs: List of scraped jobs
            
        Returns:
            List of normalized, deduplicated jobs
        """
        normalized_jobs = []
        
        for job in jobs:
            # Normalize job data
            normalized_job = normalize_job_data(job)
            
            # Check for duplicates
            if not self.deduplicator.is_duplicate(normalized_job):
                normalized_jobs.append(normalized_job)
                self.deduplicator.add_job(normalized_job)
                
        logger.info(f"Normalized {len(normalized_jobs)} jobs, removed {len(jobs) - len(normalized_jobs)} duplicates")
        return normalized_jobs
    
    async def export_to_backend(self, jobs: List[ScrapedJob]) -> bool:
        """
        Export jobs to backend via POST /jobs/import
        
        Args:
            jobs: List of jobs to export
            
        Returns:
            Success status
        """
        if not jobs:
            logger.info("No jobs to export")
            return True
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Convert jobs to dictionary format
            jobs_dict = [asdict(job) for job in jobs]
            
            async with self.session.post(
                f"{self.backend_url}/api/jobs/import",
                headers=headers,
                json=jobs_dict
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"Successfully exported {len(jobs)} jobs to backend: {result}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to export jobs: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error exporting jobs to backend: {str(e)}")
            return False
    
    async def run_full_scraping_cycle(self, sources_config: List[Dict]) -> Dict[str, Any]:
        """
        Run a complete scraping cycle: scrape -> normalize -> dedupe -> export
        
        Args:
            sources_config: List of source configurations
            
        Returns:
            Summary of the scraping cycle
        """
        start_time = datetime.utcnow()
        logger.info("Starting full scraping cycle")
        
        # 1. Scrape jobs from all sources
        scraped_jobs = await self.scrape_all_sources(sources_config)
        logger.info(f"Scraped {len(scraped_jobs)} jobs from all sources")
        
        # 2. Normalize and deduplicate
        normalized_jobs = self.normalize_and_dedupe(scraped_jobs)
        logger.info(f"After normalization and deduplication: {len(normalized_jobs)} jobs")
        
        # 3. Export to backend
        export_success = await self.export_to_backend(normalized_jobs)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            'scraped_count': len(scraped_jobs),
            'normalized_count': len(normalized_jobs),
            'export_success': export_success,
            'duration_seconds': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        logger.info(f"Scraping cycle completed in {duration:.2f} seconds")
        return summary
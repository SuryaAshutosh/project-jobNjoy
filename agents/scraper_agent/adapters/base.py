"""
Base adapter class for job scraping adapters
"""

import asyncio
import random
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

class BaseAdapter(ABC):
    """Abstract base class for job scraping adapters"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        self.session = session
        self.proxy_manager = proxy_manager
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
    async def _make_request(self, url: str, method: str = 'GET', **kwargs) -> aiohttp.ClientResponse:
        """
        Make HTTP request with proxy rotation and user agent rotation
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for the request
            
        Returns:
            HTTP response
        """
        # Add randomized delay to avoid rate limiting
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Set headers with random user agent
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = random.choice(self.user_agents)
        kwargs['headers'] = headers
        
        # Add proxy if available
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                kwargs['proxy'] = proxy
                
        # Make request
        async with self.session.request(method, url, **kwargs) as response:
            return response
            
    def _detect_captcha(self, content: str) -> bool:
        """
        Simple heuristic to detect CAPTCHA challenges
        
        Args:
            content: Page content
            
        Returns:
            True if CAPTCHA detected
        """
        captcha_indicators = [
            'recaptcha',
            'captcha',
            'challenge',
            'security check',
            'verify you are human',
            'are you a robot',
            'click verify',
            'solve challenge'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in captcha_indicators)
        
    @abstractmethod
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from the source
        
        Args:
            params: Search parameters (keyword, location, etc.)
            
        Returns:
            List of job dictionaries
        """
        pass
        
    def _calculate_confidence(self, job_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        required_fields = ['title', 'company', 'description']
        optional_fields = ['url', 'location', 'salary_min', 'salary_max', 'posted_date']
        
        required_present = sum(1 for field in required_fields if job_data.get(field))
        optional_present = sum(1 for field in optional_fields if job_data.get(field))
        
        # Weight required fields more heavily
        confidence = (required_present / len(required_fields)) * 0.7 + \
                     (optional_present / len(optional_fields)) * 0.3
                     
        return round(confidence, 2)
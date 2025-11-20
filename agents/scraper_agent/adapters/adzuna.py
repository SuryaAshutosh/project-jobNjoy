"""
Adzuna job scraping adapter
Uses the official Adzuna API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class AdzunaAdapter(BaseAdapter):
    """Adzuna job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        # These would typically come from environment variables
        self.app_id = "YOUR_APP_ID"
        self.app_key = "YOUR_APP_KEY"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Adzuna API
        
        Args:
            params: Search parameters (keyword, location, etc.)
            
        Returns:
            List of job dictionaries
        """
        keyword = params.get('keyword', '')
        location = params.get('location', '')
        page = params.get('page', 1)
        per_page = params.get('per_page', 50)
        max_pages = params.get('max_pages', 3)
        
        jobs = []
        
        try:
            # Build search parameters
            search_params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': per_page,
                'what': keyword,
                'where': location,
                'content-type': 'application/json'
            }
            
            # Add optional filters
            if 'salary_min' in params:
                search_params['salary_min'] = params['salary_min']
                
            if 'job_type' in params:
                search_params['full_time'] = 1 if params['job_type'] == 'fulltime' else 0
                
            if params.get('remote', False):
                search_params['remote'] = 1
                
            # Fetch jobs for multiple pages
            for page_num in range(page, page + max_pages):
                search_params['page'] = page_num
                
                url = f"{self.base_url}/gb/search/{page_num}?{urlencode(search_params)}"
                
                try:
                    response = await self._make_request(url)
                    
                    if response.status == 200:
                        data = await response.json()
                        page_jobs = self._parse_api_response(data)
                        jobs.extend(page_jobs)
                        
                        # If we got fewer jobs than requested, we've reached the end
                        if len(page_jobs) < per_page:
                            break
                            
                    elif response.status == 429:
                        # Rate limited, wait and retry
                        await asyncio.sleep(5)
                        response = await self._make_request(url)
                        if response.status == 200:
                            data = await response.json()
                            jobs.extend(self._parse_api_response(data))
                            
                except Exception as e:
                    print(f"Error fetching page {page_num} from Adzuna: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Adzuna: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Adzuna API response into standardized job format
        
        Args:
            data: API response data
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if 'results' not in data:
            return jobs
            
        for item in data['results']:
            try:
                # Extract salary information
                salary_min = item.get('salary_min')
                salary_max = item.get('salary_max')
                
                # Extract location
                location = ""
                if 'location' in item and 'display_name' in item['location']:
                    location = item['location']['display_name']
                    
                # Extract company
                company = ""
                if 'company' in item and 'display_name' in item['company']:
                    company = item['company']['display_name']
                    
                # Extract posted date
                posted_date = item.get('created')
                
                job_data = {
                    'source_name': 'adzuna',
                    'source_id': str(item.get('id', '')),
                    'title': item.get('title', '').strip(),
                    'company': company.strip(),
                    'url': item.get('redirect_url', ''),
                    'description': item.get('description', '').strip(),
                    'skills': item.get('skills', []),
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'location': location.strip(),
                    'posted_date': posted_date,
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Adzuna: {e}")
                continue
                
        return jobs
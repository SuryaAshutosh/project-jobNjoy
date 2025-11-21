"""
Jooble job scraping adapter
Uses the official Jooble API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class JoobleAdapter(BaseAdapter):
    """Jooble job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://jooble.org/api"
        # API key would typically come from environment variables
        self.api_key = "YOUR_JOOBLE_API_KEY"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Jooble API
        
        Args:
            params: Search parameters (keyword, location, etc.)
            
        Returns:
            List of job dictionaries
        """
        keyword = params.get('keyword', '')
        location = params.get('location', '')
        page = params.get('page', 1)
        max_pages = params.get('max_pages', 3)
        
        jobs = []
        
        try:
            # Build search parameters
            search_params = {
                "keywords": keyword,
                "location": location
            }
            
            # Add optional filters
            if 'salary_min' in params:
                search_params['salary'] = params['salary_min']
                
            if params.get('remote', False):
                search_params['remote'] = True
                
            # Fetch jobs for multiple pages
            for page_num in range(page, page + max_pages):
                search_params['page'] = page_num
                
                url = f"{self.base_url}/{self.api_key}"
                
                try:
                    # Jooble API expects POST requests with JSON body
                    response = await self._make_request(
                        url, 
                        method='POST',
                        json=search_params
                    )
                    
                    if response.status == 200:
                        data = await response.json()
                        page_jobs = self._parse_api_response(data)
                        jobs.extend(page_jobs)
                        
                        # If we got fewer jobs than expected, we've reached the end
                        if len(page_jobs) < 20:  # Jooble default is 20 per page
                            break
                            
                    elif response.status == 429:
                        # Rate limited, wait and retry
                        await asyncio.sleep(5)
                        response = await self._make_request(
                            url,
                            method='POST',
                            json=search_params
                        )
                        if response.status == 200:
                            data = await response.json()
                            jobs.extend(self._parse_api_response(data))
                            
                except Exception as e:
                    print(f"Error fetching page {page_num} from Jooble: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Jooble: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Jooble API response into standardized job format
        
        Args:
            data: API response data
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if 'jobs' not in data:
            return jobs
            
        for item in data['jobs']:
            try:
                # Extract salary information
                salary = item.get('salary', '')
                salary_min = None
                salary_max = None
                
                # Try to parse salary if it's a string like "$50,000 - $70,000"
                if isinstance(salary, str) and '-' in salary:
                    parts = salary.split('-')
                    if len(parts) == 2:
                        try:
                            salary_min = int(''.join(filter(str.isdigit, parts[0])))
                            salary_max = int(''.join(filter(str.isdigit, parts[1])))
                        except ValueError:
                            pass
                elif isinstance(salary, str):
                    try:
                        salary_min = int(''.join(filter(str.isdigit, salary)))
                    except ValueError:
                        pass
                        
                job_data = {
                    'source_name': 'jooble',
                    'source_id': str(item.get('id', '')),
                    'title': item.get('title', '').strip(),
                    'company': item.get('company', '').strip(),
                    'url': item.get('link', ''),
                    'description': item.get('snippet', '').strip(),
                    'skills': [],  # Jooble doesn't provide skills directly
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'location': item.get('location', '').strip(),
                    'posted_date': item.get('updated', ''),  # Using updated date
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Jooble: {e}")
                continue
                
        return jobs
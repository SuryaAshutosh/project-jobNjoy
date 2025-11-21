"""
Careerjet job scraping adapter
Uses the official Careerjet API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class CareerjetAdapter(BaseAdapter):
    """Careerjet job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "http://www.careerjet.com/search/jobs"
        # API key would typically come from environment variables
        self.api_key = "YOUR_CAREERJET_API_KEY"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Careerjet API
        
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
                "location": location,
                "affid": self.api_key,
                "page": page,
                "pagesize": 20  # Careerjet default page size
            }
            
            # Add optional filters
            if params.get('salary_min'):
                search_params['salary'] = params['salary_min']
                
            # Fetch jobs for multiple pages
            for page_num in range(page, page + max_pages):
                search_params['page'] = page_num
                
                url = f"{self.base_url}?{urlencode(search_params)}"
                
                try:
                    response = await self._make_request(url)
                    
                    if response.status == 200:
                        data = await response.json()
                        page_jobs = self._parse_api_response(data)
                        jobs.extend(page_jobs)
                        
                        # If we got fewer jobs than expected, we've reached the end
                        if len(page_jobs) < 20:  # Careerjet default is 20 per page
                            break
                            
                    elif response.status == 429:
                        # Rate limited, wait and retry
                        await asyncio.sleep(5)
                        response = await self._make_request(url)
                        if response.status == 200:
                            data = await response.json()
                            jobs.extend(self._parse_api_response(data))
                            
                except Exception as e:
                    print(f"Error fetching page {page_num} from Careerjet: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Careerjet: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Careerjet API response into standardized job format
        
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
                        
                # Extract date
                date = item.get('date', '')
                
                job_data = {
                    'source_name': 'careerjet',
                    'source_id': str(item.get('url', '')),  # Using URL as ID since Careerjet doesn't provide IDs
                    'title': item.get('title', '').strip(),
                    'company': item.get('company', '').strip(),
                    'url': item.get('url', ''),
                    'description': item.get('description', '').strip(),
                    'skills': [],  # Careerjet doesn't provide skills directly
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'location': item.get('locations', '').strip(),
                    'posted_date': date,
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Careerjet: {e}")
                continue
                
        return jobs
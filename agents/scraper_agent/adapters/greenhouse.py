"""
Greenhouse job scraping adapter
Uses the official Greenhouse API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class GreenhouseAdapter(BaseAdapter):
    """Greenhouse job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://boards-api.greenhouse.io/v1/boards"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Greenhouse API
        
        Args:
            params: Search parameters (board_token is required)
            
        Returns:
            List of job dictionaries
        """
        board_token = params.get('board_token')
        if not board_token:
            raise ValueError("board_token is required for Greenhouse API")
            
        jobs = []
        
        try:
            url = f"{self.base_url}/{board_token}/jobs"
            
            # Add query parameters
            query_params = {}
            if params.get('content', False):
                query_params['content'] = 'true'
                
            if query_params:
                url += "?" + urlencode(query_params)
                
            response = await self._make_request(url)
            
            if response.status == 200:
                data = await response.json()
                jobs = self._parse_api_response(data, board_token)
            elif response.status == 429:
                # Rate limited, wait and retry
                await asyncio.sleep(5)
                response = await self._make_request(url)
                if response.status == 200:
                    data = await response.json()
                    jobs = self._parse_api_response(data, board_token)
                    
        except Exception as e:
            print(f"Error scraping Greenhouse: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: Dict[str, Any], board_token: str) -> List[Dict[str, Any]]:
        """
        Parse Greenhouse API response into standardized job format
        
        Args:
            data: API response data
            board_token: Board token used for the request
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        if 'jobs' not in data:
            return jobs
            
        for item in data['jobs']:
            try:
                # Extract location
                location = ""
                if item.get('location', {}).get('name'):
                    location = item['location']['name']
                elif item.get('offices'):
                    # Get location from offices if available
                    office_locations = [office.get('location') for office in item['offices'] if office.get('location')]
                    location = ", ".join(filter(None, office_locations))
                    
                # Extract departments
                departments = [dept.get('name') for dept in item.get('departments', []) if dept.get('name')]
                
                job_data = {
                    'source_name': 'greenhouse',
                    'source_id': str(item.get('id', '')),
                    'title': item.get('title', '').strip(),
                    'company': item.get('company_name', '').strip() or board_token,
                    'url': item.get('absolute_url', ''),
                    'description': item.get('content', '').strip(),
                    'skills': departments,  # Using departments as skills
                    'salary_min': None,  # Greenhouse doesn't provide salary info
                    'salary_max': None,
                    'location': location.strip(),
                    'posted_date': item.get('updated_at'),  # Using updated_at date
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Greenhouse: {e}")
                continue
                
        return jobs
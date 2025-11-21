"""
Workable job scraping adapter
Uses the official Workable API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class WorkableAdapter(BaseAdapter):
    """Workable job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://apply.workable.com/api/v1/widget/accounts"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Workable API
        
        Args:
            params: Search parameters (clientname is required)
            
        Returns:
            List of job dictionaries
        """
        clientname = params.get('clientname')
        if not clientname:
            raise ValueError("clientname is required for Workable API")
            
        jobs = []
        
        try:
            url = f"{self.base_url}/{clientname}/jobs"
            
            # Add query parameters
            query_params = {}
            if params.get('limit'):
                query_params['limit'] = params['limit']
                
            if query_params:
                url += "?" + urlencode(query_params)
                
            response = await self._make_request(url)
            
            if response.status == 200:
                data = await response.json()
                jobs = self._parse_api_response(data, clientname)
            elif response.status == 429:
                # Rate limited, wait and retry
                await asyncio.sleep(5)
                response = await self._make_request(url)
                if response.status == 200:
                    data = await response.json()
                    jobs = self._parse_api_response(data, clientname)
                    
        except Exception as e:
            print(f"Error scraping Workable: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: Dict[str, Any], clientname: str) -> List[Dict[str, Any]]:
        """
        Parse Workable API response into standardized job format
        
        Args:
            data: API response data
            clientname: Client name used for the request
            
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
                if item.get('location'):
                    location = item['location']
                elif item.get('remote'):
                    location = "Remote"
                    
                # Extract department
                department = item.get('department', '')
                
                # Extract employment type
                employment_type = item.get('employment_type', '')
                
                # Combine department and employment type as skills
                skills = []
                if department:
                    skills.append(department)
                if employment_type:
                    skills.append(employment_type)
                
                job_data = {
                    'source_name': 'workable',
                    'source_id': str(item.get('shortcode', '')),
                    'title': item.get('title', '').strip(),
                    'company': clientname,
                    'url': item.get('url', ''),
                    'description': item.get('description', '').strip(),
                    'skills': skills,
                    'salary_min': None,  # Workable doesn't provide salary info
                    'salary_max': None,
                    'location': location.strip(),
                    'posted_date': item.get('published_on'),  # Using published_on date
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Workable: {e}")
                continue
                
        return jobs
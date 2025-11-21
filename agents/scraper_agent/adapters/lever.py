"""
Lever job scraping adapter
Uses the official Lever API for job listings
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from adapters.base import BaseAdapter

class LeverAdapter(BaseAdapter):
    """Lever job scraping adapter using official API"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://api.lever.co/v0/postings"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Lever API
        
        Args:
            params: Search parameters (clientname is required)
            
        Returns:
            List of job dictionaries
        """
        clientname = params.get('clientname')
        if not clientname:
            raise ValueError("clientname is required for Lever API")
            
        jobs = []
        
        try:
            url = f"{self.base_url}/{clientname}"
            
            # Add query parameters
            query_params = {}
            if params.get('mode') in ['json', 'iframe']:
                query_params['mode'] = params['mode']
                
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
            print(f"Error scraping Lever: {e}")
            
        return jobs
        
    def _parse_api_response(self, data: List[Dict[str, Any]], clientname: str) -> List[Dict[str, Any]]:
        """
        Parse Lever API response into standardized job format
        
        Args:
            data: API response data (list of jobs)
            clientname: Client name used for the request
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        for item in data:
            try:
                # Extract location
                location = ""
                if isinstance(item.get('categories'), dict):
                    location = item['categories'].get('location', '')
                    
                # Extract commitment (job type)
                commitment = ""
                if isinstance(item.get('categories'), dict):
                    commitment = item['categories'].get('commitment', '')
                    
                # Extract teams/departments
                teams = []
                if isinstance(item.get('categories'), dict):
                    if item['categories'].get('team'):
                        teams.append(item['categories']['team'])
                    if item['categories'].get('department'):
                        teams.append(item['categories']['department'])
                
                # Create description from text sections
                description_parts = []
                if isinstance(item.get('descriptionPlain'), str):
                    description_parts.append(item['descriptionPlain'])
                elif isinstance(item.get('description'), str):
                    description_parts.append(item['description'])
                    
                description = "\n\n".join(description_parts)
                
                job_data = {
                    'source_name': 'lever',
                    'source_id': str(item.get('id', '')),
                    'title': item.get('text', '').strip(),
                    'company': clientname,
                    'url': item.get('hostedUrl', ''),
                    'description': description.strip(),
                    'skills': teams,  # Using teams/departments as skills
                    'salary_min': None,  # Lever doesn't provide salary info
                    'salary_max': None,
                    'location': location.strip(),
                    'posted_date': None,  # Lever doesn't provide posting dates
                    'raw_payload': item,
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                jobs.append(job_data)
                
            except Exception as e:
                print(f"Error parsing job from Lever: {e}")
                continue
                
        return jobs
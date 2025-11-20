"""
LinkedIn job scraping adapter
Supports both API and scraping approaches
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from adapters.base import BaseAdapter

class LinkedInAdapter(BaseAdapter):
    """LinkedIn job scraping adapter"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://www.linkedin.com"
        self.api_base_url = "https://linkedin.com"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from LinkedIn
        
        Args:
            params: Search parameters (keyword, location, etc.)
            
        Returns:
            List of job dictionaries
        """
        # Try API approach first
        try:
            jobs = await self._scrape_via_api(params)
            if jobs:
                return jobs
        except Exception as e:
            print(f"API approach failed: {e}")
            
        # Fallback to scraping approach
        return await self._scrape_via_playwright(params)
        
    async def _scrape_via_api(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs using LinkedIn's unofficial API
        
        Args:
            params: Search parameters
            
        Returns:
            List of job dictionaries
        """
        # Note: LinkedIn's API requires authentication which is complex to implement
        # This is a placeholder for when API access is available
        raise NotImplementedError("LinkedIn API scraping not implemented")
        
    async def _scrape_via_playwright(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs using Playwright browser automation
        
        Args:
            params: Search parameters
            
        Returns:
            List of job dictionaries
        """
        keyword = params.get('keyword', '')
        location = params.get('location', '')
        page_limit = params.get('page_limit', 3)
        
        jobs = []
        
        try:
            async with async_playwright() as p:
                # Launch browser with appropriate settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                # Create context with user agent
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = await context.new_page()
                
                # Navigate to LinkedIn jobs search
                search_url = f"{self.base_url}/jobs/search/?keywords={keyword}&location={location}"
                await page.goto(search_url)
                
                # Wait for job listings to load
                await page.wait_for_selector('.jobs-search-results-list', timeout=10000)
                
                # Scroll to load more jobs
                for i in range(page_limit):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    
                    # Check for CAPTCHA
                    content = await page.content()
                    if self._detect_captcha(content):
                        print("CAPTCHA detected, trying to bypass...")
                        # Try to switch proxy/user agent and retry
                        await context.close()
                        await browser.close()
                        return jobs
                        
                # Extract job listings
                job_elements = await page.query_selector_all('.job-card-container')
                
                for element in job_elements:
                    try:
                        job = await self._extract_job_details_from_element(page, element)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job details: {e}")
                        continue
                        
                await context.close()
                await browser.close()
                
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
            
        return jobs
        
    async def _extract_job_details_from_element(self, page, element) -> Optional[Dict[str, Any]]:
        """
        Extract job details from a job card element
        
        Args:
            page: Playwright page object
            element: Job card element
            
        Returns:
            Job dictionary or None
        """
        try:
            # Extract basic information
            title_elem = await element.query_selector('.job-card-list__title')
            title = await title_elem.inner_text() if title_elem else ""
            
            company_elem = await element.query_selector('.job-card-container__company-name')
            company = await company_elem.inner_text() if company_elem else ""
            
            location_elem = await element.query_selector('.job-card-container__metadata-item')
            location = await location_elem.inner_text() if location_elem else ""
            
            # Get job URL and ID
            link_elem = await element.query_selector('a')
            url = ""
            source_id = ""
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    url = f"{self.base_url}{href}" if href.startswith('/') else href
                    # Extract job ID from URL
                    match = re.search(r'/jobs/view/(\d+)/', href)
                    if match:
                        source_id = match.group(1)
                        
            # Click on job to get full details
            if link_elem:
                await link_elem.click()
                await page.wait_for_timeout(2000)
                
                # Extract full description
                description_elem = await page.query_selector('.jobs-description-content')
                description = await description_elem.inner_text() if description_elem else ""
                
                # Extract salary if available
                salary_elem = await page.query_selector('.salary-compensation__salary')
                salary_text = await salary_elem.inner_text() if salary_elem else ""
                
                # Parse salary
                salary_min, salary_max = self._parse_salary(salary_text)
                
                # Extract posted date
                date_elem = await page.query_selector('.jobs-unified-top-card__posted-date')
                posted_date = await date_elem.inner_text() if date_elem else ""
                
                job_data = {
                    'source_name': 'linkedin',
                    'source_id': source_id,
                    'title': title.strip(),
                    'company': company.strip(),
                    'url': url,
                    'description': description.strip(),
                    'skills': [],  # Would need separate extraction
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'location': location.strip(),
                    'posted_date': posted_date.strip(),
                    'raw_payload': {
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary_text,
                        'posted_date': posted_date
                    },
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                return job_data
                
        except Exception as e:
            print(f"Error extracting job details: {e}")
            
        return None
        
    def _parse_salary(self, salary_text: str) -> tuple:
        """
        Parse salary text to extract min and max values
        
        Args:
            salary_text: Salary text string
            
        Returns:
            Tuple of (min_salary, max_salary)
        """
        if not salary_text:
            return None, None
            
        # Remove non-numeric characters except dashes and dots
        cleaned = re.sub(r'[^\d\-\.kKmM]', '', salary_text)
        
        # Handle ranges like "80K-120K"
        if '-' in cleaned:
            parts = cleaned.split('-')
            try:
                min_val = self._convert_salary_value(parts[0])
                max_val = self._convert_salary_value(parts[1])
                return min_val, max_val
            except:
                pass
                
        # Handle single values
        try:
            val = self._convert_salary_value(cleaned)
            return val, val
        except:
            pass
            
        return None, None
        
    def _convert_salary_value(self, value_str: str) -> int:
        """
        Convert salary string to integer value
        
        Args:
            value_str: Salary value string
            
        Returns:
            Integer salary value
        """
        if not value_str:
            return None
            
        # Handle K and M multipliers
        multiplier = 1
        if 'k' in value_str.lower():
            multiplier = 1000
            value_str = value_str.lower().replace('k', '')
        elif 'm' in value_str.lower():
            multiplier = 1000000
            value_str = value_str.lower().replace('m', '')
            
        # Convert to integer
        try:
            value = float(value_str)
            return int(value * multiplier)
        except:
            return None
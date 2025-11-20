"""
Naukri job scraping adapter
Specifically for the Indian job market
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

class NaukriAdapter(BaseAdapter):
    """Naukri job scraping adapter for Indian job market"""
    
    def __init__(self, session: aiohttp.ClientSession, proxy_manager=None):
        super().__init__(session, proxy_manager)
        self.base_url = "https://www.naukri.com"
        
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Naukri
        
        Args:
            params: Search parameters (keyword, location, etc.)
            
        Returns:
            List of job dictionaries
        """
        return await self._scrape_via_playwright(params)
        
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
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = await context.new_page()
                
                # Navigate to Naukri jobs search
                # Naukri uses a specific search URL format
                search_url = f"{self.base_url}/jobsv2?q={keyword}&l={location}&clusterId=0"
                await page.goto(search_url)
                
                # Wait for job listings to load
                await page.wait_for_selector('.jobTuple', timeout=10000)
                
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
                job_elements = await page.query_selector_all('.jobTuple')
                
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
            print(f"Error scraping Naukri: {e}")
            
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
            # Extract basic information using Naukri-specific selectors
            title_elem = await element.query_selector('.title, .jobTitle')
            title = await title_elem.inner_text() if title_elem else ""
            
            company_elem = await element.query_selector('.company, .org')
            company = await company_elem.inner_text() if company_elem else ""
            
            location_elem = await element.query_selector('.location, .loc')
            location = await location_elem.inner_text() if location_elem else ""
            
            # Get job URL and ID
            link_elem = await element.query_selector('a')
            url = ""
            source_id = ""
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    url = href
                    # Extract job ID from URL
                    match = re.search(r'-jobs-(\d+)', href)
                    if match:
                        source_id = match.group(1)
                        
            # Extract salary if available
            salary_elem = await element.query_selector('.salary, .sal')
            salary_text = await salary_elem.inner_text() if salary_elem else ""
            
            # Parse salary (Naukri typically shows salary in INR)
            salary_min, salary_max = self._parse_salary(salary_text)
            
            # Extract experience if available
            exp_elem = await element.query_selector('.experience, .exp')
            experience = await exp_elem.inner_text() if exp_elem else ""
            
            # Extract posted date
            date_elem = await element.query_selector('.date, .time')
            posted_date = await date_elem.inner_text() if date_elem else ""
            
            # Click on job to get full details
            if link_elem:
                await link_elem.click()
                await page.wait_for_timeout(2000)
                
                # Extract full description
                description_elem = await page.query_selector('.job-desc, .job-description, .dDesc')
                description = await description_elem.inner_text() if description_elem else ""
                
                job_data = {
                    'source_name': 'naukri',
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
                        'experience': experience,
                        'posted_date': posted_date
                    },
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Calculate confidence score
                job_data['confidence'] = self._calculate_confidence(job_data)
                
                # Go back to search results
                await page.go_back()
                await page.wait_for_selector('.jobTuple', timeout=5000)
                
                return job_data
                
        except Exception as e:
            print(f"Error extracting job details: {e}")
            
        return None
        
    def _parse_salary(self, salary_text: str) -> tuple:
        """
        Parse salary text to extract min and max values
        Naukri typically shows salary in INR like "3-6 Lakhs PA."
        
        Args:
            salary_text: Salary text string
            
        Returns:
            Tuple of (min_salary, max_salary)
        """
        if not salary_text:
            return None, None
            
        # Remove non-numeric characters except dashes and dots
        cleaned = re.sub(r'[^\d\-\.]', '', salary_text)
        
        # Handle ranges like "3-6" (Lakhs)
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
        Convert salary string to integer value in INR
        Naukri typically shows values in Lakhs (1 Lakh = 100,000 INR)
        
        Args:
            value_str: Salary value string
            
        Returns:
            Integer salary value in INR
        """
        if not value_str:
            return None
            
        # Convert to float and multiply by 100,000 (1 Lakh)
        try:
            value = float(value_str)
            return int(value * 100000)  # Convert Lakhs to INR
        except:
            return None
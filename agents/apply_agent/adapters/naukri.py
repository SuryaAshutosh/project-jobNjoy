"""
Naukri adapter for Auto-Apply Agent
Handles Naukri-specific application processes (India-focused)
"""

import asyncio
import logging
from typing import Dict, Any
from playwright.async_api import Page
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class NaukriAdapter(BaseAdapter):
    """Naukri-specific adapter for handling job applications"""
    
    def __init__(self):
        """Initialize Naukri adapter"""
        super().__init__("naukri")
        
    async def detect_login_page(self, page: Page) -> bool:
        """
        Detect if current page is Naukri login page
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login page detected, False otherwise
        """
        try:
            # Check for Naukri login elements
            login_indicators = [
                "input[placeholder='Enter your active Email ID / Username']",
                "input[placeholder='Enter your password']",
                "Naukri Login",
                "naukri.com/nlogin/login"
            ]
            
            page_url = page.url.lower()
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check URL
            if "naukri.com/nlogin/login" in page_url:
                logger.info("Naukri login page detected by URL")
                return True
                
            # Check for login elements
            for selector in login_indicators[:2]:  # Check first two selectors
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"Naukri login page detected by element: {selector}")
                    return True
                    
            # Check page content
            for indicator in login_indicators[2:]:  # Check content indicators
                if indicator.lower() in page_content_lower:
                    logger.info(f"Naukri login page detected by content: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting Naukri login page: {e}")
            return False
            
    async def handle_login(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Handle Naukri login process
        
        Args:
            page: Playwright page object
            credentials: Login credentials (email, password)
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            email = credentials.get("email", "")
            password = credentials.get("password", "")
            
            if not email or not password:
                logger.error("Missing email or password for Naukri login")
                return False
                
            # Fill email field
            email_field = await page.query_selector("input[placeholder='Enter your active Email ID / Username']")
            if email_field:
                await email_field.fill(email)
                logger.info("Filled Naukri email field")
            else:
                logger.error("Could not find Naukri email field")
                return False
                
            # Fill password field
            password_field = await page.query_selector("input[placeholder='Enter your password']")
            if password_field:
                await password_field.fill(password)
                logger.info("Filled Naukri password field")
            else:
                logger.error("Could not find Naukri password field")
                return False
                
            # Click login button
            login_button = await page.query_selector("button[type='submit']")
            if login_button:
                await login_button.click()
                logger.info("Clicked Naukri login button")
            else:
                logger.error("Could not find Naukri login button")
                return False
                
            # Wait for navigation or error
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
                
            # Check if login was successful
            if await self._is_logged_in(page):
                logger.info("Naukri login successful")
                return True
            else:
                logger.error("Naukri login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error handling Naukri login: {e}")
            return False
            
    async def _is_logged_in(self, page: Page) -> bool:
        """
        Check if user is logged into Naukri
        
        Args:
            page: Playwright page object
            
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Look for user account elements
            account_indicators = [
                "div.logged-in-user",
                "a#logoutLink",
                "div.user-name"
            ]
            
            for selector in account_indicators:
                element = await page.query_selector(selector)
                if element:
                    return True
                    
            # Check URL
            if "naukri.com" in page.url and "nlogin" not in page.url:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error checking Naukri login status: {e}")
            return False
            
    async def detect_application_form(self, page: Page) -> bool:
        """
        Detect if current page contains Naukri application form
        
        Args:
            page: Playwright page object
            
        Returns:
            True if application form detected, False otherwise
        """
        try:
            # Look for Naukri application elements
            form_indicators = [
                "form#applyForm",
                "div.applyWidget",
                "button#applyButton",
                "input[type='file'][id='attachCV']"
            ]
            
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check for form elements
            for selector in form_indicators:
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"Naukri application form detected by element: {selector}")
                    return True
                    
            # Check page content for application keywords
            application_keywords = ["apply now", "upload resume", "submit application", "apply for job"]
            for keyword in application_keywords:
                if keyword in page_content_lower:
                    logger.info(f"Naukri application form detected by keyword: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting Naukri application form: {e}")
            return False
            
    async def handle_multi_step_application(self, page: Page, max_steps: int = 3) -> bool:
        """
        Handle Naukri's multi-step application process
        
        Args:
            page: Playwright page object
            max_steps: Maximum number of steps to handle
            
        Returns:
            True if application process completed, False otherwise
        """
        try:
            step = 1
            
            while step <= max_steps:
                logger.info(f"Handling Naukri application step {step}")
                
                # Wait for page to stabilize
                await self.wait_for_network_idle(page)
                await self.wait_for_dom_stable(page)
                
                # Check for CAPTCHA
                page_content = await self.get_page_text(page)
                if self.detect_captcha(page_content):
                    logger.warning("CAPTCHA detected during Naukri application")
                    return False
                    
                # Look for submit button first (last step)
                submit_button = await page.query_selector("button#submitApplication")
                if submit_button:
                    logger.info("Found submit button, completing application")
                    await submit_button.click()
                    
                    # Wait for confirmation
                    try:
                        await page.wait_for_selector("div.success-message", timeout=10000)
                        logger.info("Naukri application submitted successfully")
                        return True
                    except:
                        logger.warning("Application submitted but no confirmation received")
                        return True
                        
                # Look for apply button
                apply_button = await page.query_selector("button#applyButton")
                if apply_button:
                    await apply_button.click()
                    logger.info("Clicked apply button")
                else:
                    # Look for next button
                    next_button = await page.query_selector("button.next-btn")
                    if next_button:
                        await next_button.click()
                        logger.info("Clicked next button")
                    else:
                        logger.warning("No apply or next button found")
                        break
                        
                # Wait a bit for next step to load
                await page.wait_for_timeout(2000)
                step += 1
                
            logger.info(f"Completed {step-1} Naukri application steps")
            return step > 1  # Return True if at least one step was processed
            
        except Exception as e:
            logger.error(f"Error handling Naukri multi-step application: {e}")
            return False
            
    async def handle_resume_upload(self, page: Page, resume_path: str) -> bool:
        """
        Handle Naukri resume upload
        
        Args:
            page: Playwright page object
            resume_path: Path to resume file
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Look for file input
            file_input = await page.query_selector("input[type='file'][id='attachCV']")
            if file_input:
                await file_input.set_input_files(resume_path)
                logger.info("Uploaded resume to Naukri")
                return True
            else:
                logger.warning("No file input found for Naukri resume upload")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading resume to Naukri: {e}")
            return False
"""
LinkedIn adapter for Auto-Apply Agent
Handles LinkedIn-specific application processes
"""

import asyncio
import logging
from typing import Dict, Any
from playwright.async_api import Page
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class LinkedInAdapter(BaseAdapter):
    """LinkedIn-specific adapter for handling job applications"""
    
    def __init__(self):
        """Initialize LinkedIn adapter"""
        super().__init__("linkedin")
        
    async def detect_login_page(self, page: Page) -> bool:
        """
        Detect if current page is LinkedIn login page
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login page detected, False otherwise
        """
        try:
            # Check for LinkedIn login elements
            login_indicators = [
                "input[name='session_key']",
                "input[name='session_password']",
                "LinkedIn Login",
                "linkedin.com/login"
            ]
            
            page_url = page.url.lower()
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check URL
            if "linkedin.com/login" in page_url:
                logger.info("LinkedIn login page detected by URL")
                return True
                
            # Check for login elements
            for selector in login_indicators[:2]:  # Check first two selectors
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"LinkedIn login page detected by element: {selector}")
                    return True
                    
            # Check page content
            for indicator in login_indicators[2:]:  # Check content indicators
                if indicator.lower() in page_content_lower:
                    logger.info(f"LinkedIn login page detected by content: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting LinkedIn login page: {e}")
            return False
            
    async def handle_login(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Handle LinkedIn login process
        
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
                logger.error("Missing email or password for LinkedIn login")
                return False
                
            # Fill email field
            email_field = await page.query_selector("input[name='session_key']")
            if email_field:
                await email_field.fill(email)
                logger.info("Filled LinkedIn email field")
            else:
                logger.error("Could not find LinkedIn email field")
                return False
                
            # Fill password field
            password_field = await page.query_selector("input[name='session_password']")
            if password_field:
                await password_field.fill(password)
                logger.info("Filled LinkedIn password field")
            else:
                logger.error("Could not find LinkedIn password field")
                return False
                
            # Click login button
            login_button = await page.query_selector("button[type='submit']")
            if login_button:
                await login_button.click()
                logger.info("Clicked LinkedIn login button")
            else:
                logger.error("Could not find LinkedIn login button")
                return False
                
            # Wait for navigation or error
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
                
            # Check if login was successful
            if await self._is_logged_in(page):
                logger.info("LinkedIn login successful")
                return True
            else:
                logger.error("LinkedIn login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error handling LinkedIn login: {e}")
            return False
            
    async def _is_logged_in(self, page: Page) -> bool:
        """
        Check if user is logged into LinkedIn
        
        Args:
            page: Playwright page object
            
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Look for user profile elements
            profile_indicators = [
                "img.profile-photo",
                "nav[aria-label='Primary Navigation']",
                "[data-control-name='nav.homepage']"
            ]
            
            for selector in profile_indicators:
                element = await page.query_selector(selector)
                if element:
                    return True
                    
            # Check URL
            if "linkedin.com/feed" in page.url or "linkedin.com/in/" in page.url:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error checking LinkedIn login status: {e}")
            return False
            
    async def detect_application_form(self, page: Page) -> bool:
        """
        Detect if current page contains LinkedIn application form
        
        Args:
            page: Playwright page object
            
        Returns:
            True if application form detected, False otherwise
        """
        try:
            # Look for LinkedIn Easy Apply elements
            form_indicators = [
                "div.jobs-apply-form",
                "button[aria-label='Submit application']",
                "div.jobs-easy-apply-modal",
                "input[name='file']"  # Resume upload field
            ]
            
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check for form elements
            for selector in form_indicators:
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"LinkedIn application form detected by element: {selector}")
                    return True
                    
            # Check page content for application keywords
            application_keywords = ["easy apply", "submit application", "upload resume"]
            for keyword in application_keywords:
                if keyword in page_content_lower:
                    logger.info(f"LinkedIn application form detected by keyword: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting LinkedIn application form: {e}")
            return False
            
    async def handle_multi_step_application(self, page: Page, max_steps: int = 3) -> bool:
        """
        Handle LinkedIn's multi-step Easy Apply process
        
        Args:
            page: Playwright page object
            max_steps: Maximum number of steps to handle
            
        Returns:
            True if application process completed, False otherwise
        """
        try:
            step = 1
            
            while step <= max_steps:
                logger.info(f"Handling LinkedIn application step {step}")
                
                # Wait for page to stabilize
                await self.wait_for_network_idle(page)
                await self.wait_for_dom_stable(page)
                
                # Check for CAPTCHA
                page_content = await self.get_page_text(page)
                if self.detect_captcha(page_content):
                    logger.warning("CAPTCHA detected during LinkedIn application")
                    return False
                    
                # Look for submit button first (last step)
                submit_button = await page.query_selector("button[aria-label='Submit application']")
                if submit_button:
                    logger.info("Found submit button, completing application")
                    await submit_button.click()
                    
                    # Wait for confirmation
                    try:
                        await page.wait_for_selector("div.artdeco-modal__content", timeout=10000)
                        logger.info("LinkedIn application submitted successfully")
                        return True
                    except:
                        logger.warning("Application submitted but no confirmation received")
                        return True
                        
                # Look for next button
                next_button = await page.query_selector("button[aria-label='Continue to next step']")
                if next_button:
                    await next_button.click()
                    logger.info("Clicked next button")
                else:
                    # Look for review button
                    review_button = await page.query_selector("button[aria-label='Review your application']")
                    if review_button:
                        await review_button.click()
                        logger.info("Clicked review button")
                    else:
                        logger.warning("No next or review button found")
                        break
                        
                # Wait a bit for next step to load
                await page.wait_for_timeout(2000)
                step += 1
                
            logger.info(f"Completed {step-1} LinkedIn application steps")
            return step > 1  # Return True if at least one step was processed
            
        except Exception as e:
            logger.error(f"Error handling LinkedIn multi-step application: {e}")
            return False
            
    async def handle_resume_upload(self, page: Page, resume_path: str) -> bool:
        """
        Handle LinkedIn resume upload
        
        Args:
            page: Playwright page object
            resume_path: Path to resume file
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Look for file input
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(resume_path)
                logger.info("Uploaded resume to LinkedIn")
                return True
            else:
                logger.warning("No file input found for LinkedIn resume upload")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading resume to LinkedIn: {e}")
            return False
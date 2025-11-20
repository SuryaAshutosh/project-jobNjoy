"""
Indeed adapter for Auto-Apply Agent
Handles Indeed-specific application processes
"""

import asyncio
import logging
from typing import Dict, Any
from playwright.async_api import Page
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class IndeedAdapter(BaseAdapter):
    """Indeed-specific adapter for handling job applications"""
    
    def __init__(self):
        """Initialize Indeed adapter"""
        super().__init__("indeed")
        
    async def detect_login_page(self, page: Page) -> bool:
        """
        Detect if current page is Indeed login page
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login page detected, False otherwise
        """
        try:
            # Check for Indeed login elements
            login_indicators = [
                "input[name='email']",
                "input[name='password']",
                "Indeed Login",
                "secure.indeed.com/account/login"
            ]
            
            page_url = page.url.lower()
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check URL
            if "secure.indeed.com/account/login" in page_url:
                logger.info("Indeed login page detected by URL")
                return True
                
            # Check for login elements
            for selector in login_indicators[:2]:  # Check first two selectors
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"Indeed login page detected by element: {selector}")
                    return True
                    
            # Check page content
            for indicator in login_indicators[2:]:  # Check content indicators
                if indicator.lower() in page_content_lower:
                    logger.info(f"Indeed login page detected by content: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting Indeed login page: {e}")
            return False
            
    async def handle_login(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Handle Indeed login process
        
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
                logger.error("Missing email or password for Indeed login")
                return False
                
            # Fill email field
            email_field = await page.query_selector("input[name='email']")
            if email_field:
                await email_field.fill(email)
                logger.info("Filled Indeed email field")
            else:
                logger.error("Could not find Indeed email field")
                return False
                
            # Click continue button
            continue_button = await page.query_selector("button[name='continue']")
            if continue_button:
                await continue_button.click()
                logger.info("Clicked Indeed continue button")
                
                # Wait for password field to appear
                try:
                    await page.wait_for_selector("input[name='password']", timeout=5000)
                except:
                    pass
                    
            # Fill password field
            password_field = await page.query_selector("input[name='password']")
            if password_field:
                await password_field.fill(password)
                logger.info("Filled Indeed password field")
            else:
                logger.error("Could not find Indeed password field")
                return False
                
            # Click sign in button
            signin_button = await page.query_selector("button[type='submit']")
            if signin_button:
                await signin_button.click()
                logger.info("Clicked Indeed sign in button")
            else:
                logger.error("Could not find Indeed sign in button")
                return False
                
            # Wait for navigation or error
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
                
            # Check if login was successful
            if await self._is_logged_in(page):
                logger.info("Indeed login successful")
                return True
            else:
                logger.error("Indeed login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error handling Indeed login: {e}")
            return False
            
    async def _is_logged_in(self, page: Page) -> bool:
        """
        Check if user is logged into Indeed
        
        Args:
            page: Playwright page object
            
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Look for user account elements
            account_indicators = [
                "a[href='/account/']",
                "button[aria-label='User account menu']",
                "div.icl-Header-userPanel"
            ]
            
            for selector in account_indicators:
                element = await page.query_selector(selector)
                if element:
                    return True
                    
            # Check URL
            if "indeed.com" in page.url and "account" not in page.url:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error checking Indeed login status: {e}")
            return False
            
    async def detect_application_form(self, page: Page) -> bool:
        """
        Detect if current page contains Indeed application form
        
        Args:
            page: Playwright page object
            
        Returns:
            True if application form detected, False otherwise
        """
        try:
            # Look for Indeed application elements
            form_indicators = [
                "form#jobsearch-IndeedApplyForm",
                "div#IA-IndeedApplyModal",
                "button#form-action-continue",
                "input[type='file'][name='resume']"
            ]
            
            page_content = await self.get_page_text(page)
            page_content_lower = page_content.lower()
            
            # Check for form elements
            for selector in form_indicators:
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"Indeed application form detected by element: {selector}")
                    return True
                    
            # Check page content for application keywords
            application_keywords = ["indeed apply", "apply now", "upload resume", "submit application"]
            for keyword in application_keywords:
                if keyword in page_content_lower:
                    logger.info(f"Indeed application form detected by keyword: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error detecting Indeed application form: {e}")
            return False
            
    async def handle_multi_step_application(self, page: Page, max_steps: int = 3) -> bool:
        """
        Handle Indeed's multi-step application process
        
        Args:
            page: Playwright page object
            max_steps: Maximum number of steps to handle
            
        Returns:
            True if application process completed, False otherwise
        """
        try:
            step = 1
            
            while step <= max_steps:
                logger.info(f"Handling Indeed application step {step}")
                
                # Wait for page to stabilize
                await self.wait_for_network_idle(page)
                await self.wait_for_dom_stable(page)
                
                # Check for CAPTCHA
                page_content = await self.get_page_text(page)
                if self.detect_captcha(page_content):
                    logger.warning("CAPTCHA detected during Indeed application")
                    return False
                    
                # Look for submit button first (last step)
                submit_button = await page.query_selector("button#form-action-submit")
                if submit_button:
                    logger.info("Found submit button, completing application")
                    await submit_button.click()
                    
                    # Wait for confirmation
                    try:
                        await page.wait_for_selector("div#ia-confirmation-screen", timeout=10000)
                        logger.info("Indeed application submitted successfully")
                        return True
                    except:
                        logger.warning("Application submitted but no confirmation received")
                        return True
                        
                # Look for continue button
                continue_button = await page.query_selector("button#form-action-continue")
                if continue_button:
                    await continue_button.click()
                    logger.info("Clicked continue button")
                else:
                    logger.warning("No continue button found")
                    break
                        
                # Wait a bit for next step to load
                await page.wait_for_timeout(2000)
                step += 1
                
            logger.info(f"Completed {step-1} Indeed application steps")
            return step > 1  # Return True if at least one step was processed
            
        except Exception as e:
            logger.error(f"Error handling Indeed multi-step application: {e}")
            return False
            
    async def handle_resume_upload(self, page: Page, resume_path: str) -> bool:
        """
        Handle Indeed resume upload
        
        Args:
            page: Playwright page object
            resume_path: Path to resume file
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Look for file input
            file_input = await page.query_selector("input[type='file'][name='resume']")
            if file_input:
                await file_input.set_input_files(resume_path)
                logger.info("Uploaded resume to Indeed")
                return True
            else:
                logger.warning("No file input found for Indeed resume upload")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading resume to Indeed: {e}")
            return False
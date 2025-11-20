"""
Base adapter for Auto-Apply Agent
Abstract base class for site-specific adapters
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from playwright.async_api import Page
from ..utils.settings import settings

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """Abstract base class for site-specific adapters"""
    
    def __init__(self, site_name: str):
        """
        Initialize base adapter
        
        Args:
            site_name: Name of the job site
        """
        self.site_name = site_name
        self.site_config = settings.get(f"sites.{site_name}", {})
        self.max_steps = self.site_config.get("max_steps", 3)
        self.login_url = self.site_config.get("login_url", "")
        
    @abstractmethod
    async def detect_login_page(self, page: Page) -> bool:
        """
        Detect if current page is a login page
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login page detected, False otherwise
        """
        pass
        
    @abstractmethod
    async def handle_login(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Handle login process for the site
        
        Args:
            page: Playwright page object
            credentials: Login credentials
            
        Returns:
            True if login successful, False otherwise
        """
        pass
        
    @abstractmethod
    async def detect_application_form(self, page: Page) -> bool:
        """
        Detect if current page contains an application form
        
        Args:
            page: Playwright page object
            
        Returns:
            True if application form detected, False otherwise
        """
        pass
        
    @abstractmethod
    async def handle_multi_step_application(self, page: Page, max_steps: int = 3) -> bool:
        """
        Handle multi-step application process
        
        Args:
            page: Playwright page object
            max_steps: Maximum number of steps to handle
            
        Returns:
            True if application process completed, False otherwise
        """
        pass
        
    async def wait_for_network_idle(self, page: Page, timeout: int = 30000):
        """
        Wait for network to become idle
        
        Args:
            page: Playwright page object
            timeout: Timeout in milliseconds
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"Timeout waiting for network idle: {e}")
            
    async def wait_for_dom_stable(self, page: Page, timeout: int = 30000):
        """
        Wait for DOM to become stable
        
        Args:
            page: Playwright page object
            timeout: Timeout in milliseconds
        """
        try:
            # Wait for page to load
            await page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(1000)
        except Exception as e:
            logger.warning(f"Timeout waiting for DOM stable: {e}")
            
    async def scroll_page(self, page: Page, scroll_amount: int = 1000):
        """
        Scroll page to reveal dynamic content
        
        Args:
            page: Playwright page object
            scroll_amount: Amount to scroll in pixels
        """
        try:
            # Get current scroll position
            current_position = await page.evaluate("window.scrollY")
            
            # Scroll down
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            
            # Wait for content to load
            await page.wait_for_timeout(500)
            
            # Check if we've reached the bottom
            new_position = await page.evaluate("window.scrollY")
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
            
            if new_position + viewport_height >= page_height:
                logger.info("Reached bottom of page")
            else:
                logger.info(f"Scrolled from {current_position} to {new_position}")
                
        except Exception as e:
            logger.warning(f"Error scrolling page: {e}")
            
    def detect_captcha(self, page_content: str) -> bool:
        """
        Detect CAPTCHA challenges on the page
        
        Args:
            page_content: Page content as string
            
        Returns:
            True if CAPTCHA detected, False otherwise
        """
        captcha_keywords = settings.get("captcha.detection_keywords", [
            "recaptcha", "captcha", "security check", "verify you are human"
        ])
        
        content_lower = page_content.lower()
        
        for keyword in captcha_keywords:
            if keyword.lower() in content_lower:
                logger.warning(f"CAPTCHA detected with keyword: {keyword}")
                return True
                
        return False
        
    async def take_screenshot(self, page: Page, name: str = "debug") -> Optional[str]:
        """
        Take screenshot for debugging purposes
        
        Args:
            page: Playwright page object
            name: Screenshot name
            
        Returns:
            Path to screenshot or None if failed
        """
        try:
            screenshot_path = f"screenshots/{name}_{int(asyncio.get_event_loop().time())}.png"
            
            # Ensure screenshots directory exists
            import os
            os.makedirs("screenshots", exist_ok=True)
            
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved to {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
            
    async def get_page_text(self, page: Page) -> str:
        """
        Get text content of the page
        
        Args:
            page: Playwright page object
            
        Returns:
            Page text content
        """
        try:
            return await page.text_content("body") or ""
        except Exception as e:
            logger.warning(f"Error getting page text: {e}")
            return ""
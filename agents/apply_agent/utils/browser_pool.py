"""
Browser pool manager for Auto-Apply Agent
Manages a pool of Playwright browser instances for efficient reuse
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext
from .settings import settings

logger = logging.getLogger(__name__)

class BrowserPool:
    """Manages a pool of browser instances for efficient reuse"""
    
    def __init__(self, max_browsers: int = 3):
        """
        Initialize browser pool
        
        Args:
            max_browsers: Maximum number of browser instances to maintain
        """
        self.max_browsers = max_browsers
        self.browsers = []
        self.contexts = []
        self.playwright = None
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def initialize(self):
        """Initialize the browser pool"""
        try:
            self.playwright = await async_playwright().start()
            logger.info("Playwright initialized")
            
            # Create initial browser instances
            for i in range(min(self.max_browsers, 2)):  # Start with 2 browsers max
                await self._create_browser()
                
        except Exception as e:
            logger.error(f"Error initializing browser pool: {e}")
            raise
            
    async def _create_browser(self) -> Browser:
        """
        Create a new browser instance
        
        Returns:
            Browser instance
        """
        try:
            # Browser launch options
            launch_options = {
                "headless": settings.get("browser.headless", True),
                "slow_mo": settings.get("browser.slow_mo", 0),
            }
            
            # Add proxy if enabled
            if settings.get("proxy.enabled", False):
                proxy_urls = settings.get("proxy.urls", [])
                if proxy_urls:
                    # Use first proxy URL for simplicity
                    proxy_url = proxy_urls[0]
                    launch_options["proxy"] = {
                        "server": proxy_url
                    }
                    
                    # Add authentication if provided
                    proxy_username = settings.get("proxy.username", "")
                    proxy_password = settings.get("proxy.password", "")
                    if proxy_username and proxy_password:
                        launch_options["proxy"]["username"] = proxy_username
                        launch_options["proxy"]["password"] = proxy_password
            
            browser = await self.playwright.chromium.launch(**launch_options)
            self.browsers.append(browser)
            
            logger.info(f"Created browser instance {len(self.browsers)}")
            return browser
            
        except Exception as e:
            logger.error(f"Error creating browser: {e}")
            raise
            
    async def get_browser(self) -> Browser:
        """
        Get a browser instance from the pool
        
        Returns:
            Browser instance
        """
        async with self._lock:
            # If we don't have enough browsers, create one
            if len(self.browsers) < self.max_browsers:
                browser = await self._create_browser()
                return browser
                
            # Return the first available browser
            return self.browsers[0]
            
    async def get_context(self, browser: Optional[Browser] = None) -> BrowserContext:
        """
        Get a new browser context
        
        Args:
            browser: Browser instance to create context for (optional)
            
        Returns:
            Browser context
        """
        try:
            if browser is None:
                browser = await self.get_browser()
                
            # Context options
            context_options = {
                "ignore_https_errors": True,
                "viewport": {"width": 1920, "height": 1080}
            }
            
            # Add user agent
            context_options["user_agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Add stealth options if enabled
            if settings.get("browser.stealth", True):
                context_options["extra_http_headers"] = {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
            
            context = await browser.new_context(**context_options)
            
            # Add stealth scripts if enabled
            if settings.get("browser.stealth", True):
                # Hide webdriver property
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                # Hide plugins
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                """)
                
                # Hide languages
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """)
            
            self.contexts.append(context)
            logger.info("Created new browser context")
            return context
            
        except Exception as e:
            logger.error(f"Error creating browser context: {e}")
            raise
            
    async def close_context(self, context: BrowserContext):
        """
        Close a browser context
        
        Args:
            context: Browser context to close
        """
        try:
            if context in self.contexts:
                self.contexts.remove(context)
            await context.close()
            logger.info("Closed browser context")
        except Exception as e:
            logger.error(f"Error closing browser context: {e}")
            
    async def close(self):
        """Close all browsers and contexts"""
        try:
            # Close all contexts
            for context in self.contexts[:]:  # Copy list to avoid modification during iteration
                await self.close_context(context)
                
            # Close all browsers
            for browser in self.browsers[:]:  # Copy list to avoid modification during iteration
                await browser.close()
                
            # Stop playwright
            if self.playwright:
                await self.playwright.stop()
                
            logger.info("Browser pool closed")
            
        except Exception as e:
            logger.error(f"Error closing browser pool: {e}")

# Global browser pool instance
browser_pool = None

async def get_browser_pool() -> BrowserPool:
    """
    Get the global browser pool instance
    
    Returns:
        BrowserPool instance
    """
    global browser_pool
    if browser_pool is None:
        browser_pool = BrowserPool()
        await browser_pool.initialize()
    return browser_pool
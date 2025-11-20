"""
Proxy management utility for job scraping
Supports HTTP, HTTPS, and SOCKS proxies with rotation
"""

import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Proxy:
    """Proxy configuration"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"  # http, https, socks5, etc.
    
    def to_url(self) -> str:
        """Convert proxy to URL format"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

class ProxyManager:
    """Manages proxy rotation and selection"""
    
    def __init__(self, proxy_config: Optional[Dict[str, Any]] = None):
        """
        Initialize proxy manager
        
        Args:
            proxy_config: Configuration dictionary with proxy settings
        """
        self.proxies: List[Proxy] = []
        self.current_index = 0
        
        if proxy_config:
            self._load_proxies(proxy_config)
            
    def _load_proxies(self, config: Dict[str, Any]):
        """Load proxies from configuration"""
        if 'proxies' in config:
            for proxy_data in config['proxies']:
                proxy = Proxy(
                    host=proxy_data['host'],
                    port=proxy_data['port'],
                    username=proxy_data.get('username'),
                    password=proxy_data.get('password'),
                    protocol=proxy_data.get('protocol', 'http')
                )
                self.proxies.append(proxy)
                
    def add_proxy(self, proxy: Proxy):
        """Add a proxy to the pool"""
        self.proxies.append(proxy)
        
    def remove_proxy(self, proxy: Proxy):
        """Remove a proxy from the pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            
    def get_proxy(self) -> Optional[str]:
        """
        Get next proxy URL in rotation
        
        Returns:
            Proxy URL string or None if no proxies configured
        """
        if not self.proxies:
            return None
            
        # Simple round-robin rotation
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy.to_url()
        
    def get_random_proxy(self) -> Optional[str]:
        """
        Get a random proxy from the pool
        
        Returns:
            Proxy URL string or None if no proxies configured
        """
        if not self.proxies:
            return None
            
        proxy = random.choice(self.proxies)
        return proxy.to_url()
        
    def get_proxy_count(self) -> int:
        """Get the number of configured proxies"""
        return len(self.proxies)
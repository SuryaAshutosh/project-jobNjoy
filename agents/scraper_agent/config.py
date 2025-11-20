"""
Configuration for Job Scraper Agent
"""

import os
from typing import List, Dict, Any

# Backend configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
API_KEY = os.getenv('SCRAPER_API_KEY', 'your-default-api-key')

# Proxy configuration
PROXY_CONFIG = {
    "proxies": [
        # Example proxy configurations:
        # {
        #     "host": "proxy1.example.com",
        #     "port": 8080,
        #     "username": "user1",
        #     "password": "pass1",
        #     "protocol": "http"
        # },
        # {
        #     "host": "proxy2.example.com",
        #     "port": 1080,
        #     "protocol": "socks5"
        # }
    ]
}

# Job sources configuration
SOURCES_CONFIG = [
    {
        "name": "LinkedIn",
        "adapter": "linkedin",
        "adapter_class": "LinkedInAdapter",
        "params": {
            "page_limit": 3
        }
    },
    {
        "name": "Adzuna",
        "adapter": "adzuna",
        "adapter_class": "AdzunaAdapter",
        "params": {
            "max_pages": 3,
            "per_page": 50
        }
    },
    {
        "name": "Monster",
        "adapter": "monster",
        "adapter_class": "MonsterAdapter",
        "params": {
            "page_limit": 3
        }
    },
    {
        "name": "Naukri",
        "adapter": "naukri",
        "adapter_class": "NaukriAdapter",
        "params": {
            "page_limit": 3
        }
    }
]

# Scheduler configuration
SCHEDULER_CONFIG = {
    "scraping_interval": 3600,  # 1 hour in seconds
    "immediate_start": True
}

# Deduplication configuration
DEDUPLICATION_CONFIG = {
    "similarity_threshold": 92.0
}

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Skills taxonomy file path
SKILLS_TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), 'data', 'skills_taxonomy.json')
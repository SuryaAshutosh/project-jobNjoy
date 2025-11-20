"""
Example configuration for Job Scraper Agent
This file demonstrates how to configure the scraper agent for different environments
"""

# Example production configuration
PRODUCTION_CONFIG = {
    "backend_url": "https://api.yourjobbuddy.com",
    "api_key": "your-production-api-key",
    "proxy_config": {
        "proxies": [
            {
                "host": "proxy1.yourproxyprovider.com",
                "port": 8080,
                "username": "your-proxy-username",
                "password": "your-proxy-password",
                "protocol": "http"
            },
            {
                "host": "proxy2.yourproxyprovider.com",
                "port": 8080,
                "username": "your-proxy-username",
                "password": "your-proxy-password",
                "protocol": "http"
            }
        ]
    },
    "sources_config": [
        {
            "name": "LinkedIn",
            "adapter": "linkedin",
            "adapter_class": "LinkedInAdapter",
            "params": {
                "page_limit": 5,
                "delay_range": [1, 3]
            }
        },
        {
            "name": "Adzuna",
            "adapter": "adzuna",
            "adapter_class": "AdzunaAdapter",
            "params": {
                "max_pages": 5,
                "per_page": 50,
                "app_id": "your-adzuna-app-id",
                "app_key": "your-adzuna-app-key"
            }
        },
        {
            "name": "Monster",
            "adapter": "monster",
            "adapter_class": "MonsterAdapter",
            "params": {
                "page_limit": 5,
                "delay_range": [1, 2]
            }
        },
        {
            "name": "Naukri",
            "adapter": "naukri",
            "adapter_class": "NaukriAdapter",
            "params": {
                "page_limit": 5,
                "delay_range": [2, 4]
            }
        }
    ],
    "scheduler_config": {
        "scraping_interval": 7200,  # 2 hours
        "immediate_start": True
    },
    "deduplication_config": {
        "similarity_threshold": 90.0
    }
}

# Example development configuration
DEVELOPMENT_CONFIG = {
    "backend_url": "http://localhost:8000",
    "api_key": "dev-api-key",
    "proxy_config": {
        "proxies": []
    },
    "sources_config": [
        {
            "name": "Adzuna",
            "adapter": "adzuna",
            "adapter_class": "AdzunaAdapter",
            "params": {
                "max_pages": 2,
                "per_page": 10,
                "app_id": "your-adzuna-app-id",
                "app_key": "your-adzuna-app-key"
            }
        }
    ],
    "scheduler_config": {
        "scraping_interval": 300,  # 5 minutes
        "immediate_start": True
    },
    "deduplication_config": {
        "similarity_threshold": 95.0
    }
}

# Example search queries configuration
SEARCH_QUERIES = [
    {
        "keyword": "software engineer",
        "location": "San Francisco, CA",
        "remote": True
    },
    {
        "keyword": "data scientist",
        "location": "New York, NY",
        "salary_min": 100000
    },
    {
        "keyword": "product manager",
        "location": "London, UK",
        "job_type": "fulltime"
    }
]
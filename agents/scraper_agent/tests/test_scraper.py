"""
Unit tests for Job Scraper Agent
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

from core import JobScraperAgent, ScrapedJob
from utils.normalizer import normalize_job_data
from utils.deduplicator import Deduplicator
from utils.proxies import ProxyManager, Proxy

class TestJobScraperAgent(unittest.TestCase):
    """Test cases for JobScraperAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = JobScraperAgent("http://test-backend.com", "test-api-key")
        
    def test_init(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.backend_url, "http://test-backend.com")
        self.assertEqual(self.agent.api_key, "test-api-key")
        self.assertIsNone(self.agent.session)
        
    def test_scraped_job_creation(self):
        """Test ScrapedJob dataclass creation"""
        job = ScrapedJob(
            source_name="test",
            source_id="123",
            title="Test Job",
            company="Test Company",
            url="http://test.com",
            description="Test Description",
            skills=["Python", "JavaScript"],
            salary_min=50000,
            salary_max=100000,
            location="Test City",
            posted_date="2023-01-01",
            scraped_at=datetime.utcnow().isoformat(),
            confidence=0.95
        )
        
        self.assertEqual(job.source_name, "test")
        self.assertEqual(job.title, "Test Job")
        self.assertEqual(job.salary_min, 50000)

class TestNormalizer(unittest.TestCase):
    """Test cases for job data normalizer"""
    
    def test_normalize_job_data(self):
        """Test job data normalization"""
        raw_job = {
            "source_name": "test",
            "source_id": "123",
            "title": "  Software Engineer  ",
            "company": "  Tech Corp  ",
            "url": "http://test.com",
            "description": "<p>Test Description</p>",
            "skills": [],
            "salary_min": "50,000",
            "salary_max": "100,000",
            "location": "  New York, NY  ",
            "posted_date": "2023-01-01",
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        normalized = normalize_job_data(raw_job)
        
        self.assertEqual(normalized["title"], "Software Engineer")
        self.assertEqual(normalized["company"], "Tech Corp")
        self.assertEqual(normalized["location"], "New York, NY")
        self.assertEqual(normalized["salary_min"], 50000)
        self.assertEqual(normalized["salary_max"], 100000)
        self.assertEqual(normalized["description"], "Test Description")

class TestDeduplicator(unittest.TestCase):
    """Test cases for job deduplicator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.deduplicator = Deduplicator()
        
    def test_exact_duplicate_detection(self):
        """Test exact duplicate detection"""
        job1 = {
            "source_name": "linkedin",
            "source_id": "123",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Test job"
        }
        
        job2 = {
            "source_name": "linkedin",
            "source_id": "123",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Test job"
        }
        
        # First job should not be duplicate
        self.assertFalse(self.deduplicator.is_duplicate(job1))
        
        # Add first job
        self.deduplicator.add_job(job1)
        
        # Second job should be duplicate
        self.assertTrue(self.deduplicator.is_duplicate(job2))
        
    def test_fuzzy_duplicate_detection(self):
        """Test fuzzy duplicate detection"""
        job1 = {
            "source_name": "linkedin",
            "source_id": "123",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "description": "Test job"
        }
        
        job2 = {
            "source_name": "indeed",
            "source_id": "456",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "description": "Similar test job"
        }
        
        # Add first job
        self.deduplicator.add_job(job1)
        
        # Second job should be fuzzy duplicate
        self.assertTrue(self.deduplicator.is_duplicate(job2))

class TestProxyManager(unittest.TestCase):
    """Test cases for proxy manager"""
    
    def test_proxy_rotation(self):
        """Test proxy rotation"""
        proxy_config = {
            "proxies": [
                {
                    "host": "proxy1.example.com",
                    "port": 8080,
                    "username": "user1",
                    "password": "pass1",
                    "protocol": "http"
                },
                {
                    "host": "proxy2.example.com",
                    "port": 8080,
                    "protocol": "https"
                }
            ]
        }
        
        proxy_manager = ProxyManager(proxy_config)
        
        # Test getting proxies in rotation
        proxy1 = proxy_manager.get_proxy()
        proxy2 = proxy_manager.get_proxy()
        proxy3 = proxy_manager.get_proxy()  # Should rotate back to first
        
        self.assertIsNotNone(proxy1)
        self.assertIsNotNone(proxy2)
        self.assertIsNotNone(proxy3)
        self.assertEqual(proxy1, proxy3)  # Should have rotated back

if __name__ == '__main__':
    unittest.main()
"""
Tests for new job scraper adapters
"""

import unittest
from unittest.mock import AsyncMock, Mock, patch
import asyncio
import sys
import os

# Add the parent directory to the path so we can import the adapters
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.jooble import JoobleAdapter
from adapters.greenhouse import GreenhouseAdapter
from adapters.lever import LeverAdapter
from adapters.workable import WorkableAdapter

class TestJoobleAdapter(unittest.TestCase):
    """Test cases for JoobleAdapter"""
    
    def setUp(self):
        self.session = Mock()
        self.adapter = JoobleAdapter(self.session)
        
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.adapter.base_url, "https://jooble.org/api")
        self.assertEqual(self.adapter.api_key, "YOUR_JOOBLE_API_KEY")
        
    @patch('adapters.base.BaseAdapter._make_request')
    async def test_scrape_jobs(self, mock_make_request):
        """Test scraping jobs"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'jobs': [
                {
                    'id': '123',
                    'title': 'Software Engineer',
                    'company': 'Test Company',
                    'link': 'https://example.com/job/123',
                    'snippet': 'Job description',
                    'location': 'New York',
                    'updated': '2023-01-01'
                }
            ]
        })
        mock_make_request.return_value = mock_response
        
        params = {'keyword': 'software engineer', 'location': 'New York'}
        jobs = await self.adapter.scrape_jobs(params)
        
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Software Engineer')
        self.assertEqual(jobs[0]['company'], 'Test Company')

class TestGreenhouseAdapter(unittest.TestCase):
    """Test cases for GreenhouseAdapter"""
    
    def setUp(self):
        self.session = Mock()
        self.adapter = GreenhouseAdapter(self.session)
        
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.adapter.base_url, "https://boards-api.greenhouse.io/v1/boards")
        
    @patch('adapters.base.BaseAdapter._make_request')
    async def test_scrape_jobs(self, mock_make_request):
        """Test scraping jobs"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'jobs': [
                {
                    'id': 123,
                    'title': 'Software Engineer',
                    'company_name': 'Test Company',
                    'absolute_url': 'https://example.com/job/123',
                    'content': 'Job description',
                    'location': {'name': 'New York'},
                    'updated_at': '2023-01-01T00:00:00Z'
                }
            ]
        })
        mock_make_request.return_value = mock_response
        
        params = {'board_token': 'test_token'}
        jobs = await self.adapter.scrape_jobs(params)
        
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Software Engineer')
        self.assertEqual(jobs[0]['company'], 'Test Company')

class TestLeverAdapter(unittest.TestCase):
    """Test cases for LeverAdapter"""
    
    def setUp(self):
        self.session = Mock()
        self.adapter = LeverAdapter(self.session)
        
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.adapter.base_url, "https://api.lever.co/v0/postings")
        
    @patch('adapters.base.BaseAdapter._make_request')
    async def test_scrape_jobs(self, mock_make_request):
        """Test scraping jobs"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[
            {
                'id': '123',
                'text': 'Software Engineer',
                'hostedUrl': 'https://example.com/job/123',
                'descriptionPlain': 'Job description',
                'categories': {
                    'location': 'New York',
                    'department': 'Engineering'
                }
            }
        ])
        mock_make_request.return_value = mock_response
        
        params = {'clientname': 'test_client'}
        jobs = await self.adapter.scrape_jobs(params)
        
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Software Engineer')
        self.assertEqual(jobs[0]['company'], 'test_client')

class TestWorkableAdapter(unittest.TestCase):
    """Test cases for WorkableAdapter"""
    
    def setUp(self):
        self.session = Mock()
        self.adapter = WorkableAdapter(self.session)
        
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.adapter.base_url, "https://apply.workable.com/api/v1/widget/accounts")
        
    @patch('adapters.base.BaseAdapter._make_request')
    async def test_scrape_jobs(self, mock_make_request):
        """Test scraping jobs"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'jobs': [
                {
                    'shortcode': '123',
                    'title': 'Software Engineer',
                    'url': 'https://example.com/job/123',
                    'description': 'Job description',
                    'location': 'New York',
                    'department': 'Engineering',
                    'published_on': '2023-01-01'
                }
            ]
        })
        mock_make_request.return_value = mock_response
        
        params = {'clientname': 'test_client'}
        jobs = await self.adapter.scrape_jobs(params)
        
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['title'], 'Software Engineer')
        self.assertEqual(jobs[0]['company'], 'test_client')

if __name__ == '__main__':
    unittest.main()
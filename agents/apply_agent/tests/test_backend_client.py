"""
Unit tests for BackendClient
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from ..exporters.backend_client import BackendClient

@pytest.fixture
def backend_client():
    """Create a BackendClient instance for testing"""
    client = BackendClient()
    # Mock the session to avoid actual HTTP calls
    client.session = AsyncMock()
    return client

def test_generate_signature(backend_client):
    """Test signature generation"""
    payload = '{"test": "data"}'
    signature = backend_client._generate_signature(payload)
    assert isinstance(signature, str)
    assert len(signature) > 0

@pytest.mark.asyncio
async def test_get_pending_applications(backend_client):
    """Test fetching pending applications"""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[{"id": "123", "status": "pending"}])
    backend_client.session.get.return_value.__aenter__.return_value = mock_response
    
    applications = await backend_client.get_pending_applications()
    assert len(applications) == 1
    assert applications[0]["id"] == "123"

@pytest.mark.asyncio
async def test_get_pending_applications_error(backend_client):
    """Test fetching pending applications with error"""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")
    backend_client.session.get.return_value.__aenter__.return_value = mock_response
    
    applications = await backend_client.get_pending_applications()
    assert len(applications) == 0

@pytest.mark.asyncio
async def test_get_job_details(backend_client):
    """Test fetching job details"""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"id": "job123", "title": "Software Engineer"})
    backend_client.session.get.return_value.__aenter__.return_value = mock_response
    
    job_data = await backend_client.get_job_details("job123")
    assert job_data["id"] == "job123"
    assert job_data["title"] == "Software Engineer"

@pytest.mark.asyncio
async def test_get_resume_data(backend_client):
    """Test fetching resume data"""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"id": "resume123", "name": "John Doe"})
    backend_client.session.get.return_value.__aenter__.return_value = mock_response
    
    resume_data = await backend_client.get_resume_data("resume123")
    assert resume_data["id"] == "resume123"
    assert resume_data["name"] == "John Doe"

@pytest.mark.asyncio
async def test_submit_application_result(backend_client):
    """Test submitting application result"""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"status": "success"})
    backend_client.session.post.return_value.__aenter__.return_value = mock_response
    
    result = await backend_client.submit_application_result("app123", "applied", "Test notes")
    assert result == True
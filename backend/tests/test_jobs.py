"""
Tests for jobs endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_jobs():
    """Test listing jobs"""
    response = client.get("/api/jobs/")
    assert response.status_code == 200
    # Should return an empty list initially
    assert response.json() == []

def test_get_jobs_count():
    """Test getting jobs count"""
    response = client.get("/api/jobs/count")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int)

def test_list_job_sources():
    """Test listing job sources"""
    response = client.get("/api/jobs/sources/")
    assert response.status_code == 200
    # Should return an empty list initially
    assert response.json() == []

def test_get_job_not_found():
    """Test getting a non-existent job"""
    response = client.get("/api/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
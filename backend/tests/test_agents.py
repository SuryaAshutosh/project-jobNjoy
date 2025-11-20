"""
Tests for agents endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_auth_example():
    """Test the agent authentication example endpoint"""
    response = client.get("/api/agents/auth-example")
    assert response.status_code == 200
    data = response.json()
    assert "payload" in data
    assert "signature" in data
    assert "headers" in data

def test_agent_webhook_invalid_json():
    """Test agent webhook with invalid JSON"""
    response = client.post(
        "/api/agents/webhook",
        content="invalid json",
        headers={"X-Signature": "test-signature"}
    )
    assert response.status_code == 400
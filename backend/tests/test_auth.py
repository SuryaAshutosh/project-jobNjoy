"""
Tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data  # Password hash should not be returned

def test_register_duplicate_user():
    """Test registering a duplicate user"""
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "duplicate@example.com",
            "password": "testpassword123"
        }
    )
    
    # Second registration with same email
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User 2",
            "email": "duplicate@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_user():
    """Test user login"""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Test User",
            "email": "login@example.com",
            "password": "loginpassword123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "loginpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
"""
Test configuration and fixtures for JobBuddy
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.main import app
from fastapi.testclient import TestClient

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    """Create a test database and yield a session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    """Create a test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user():
    """Create a test user"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
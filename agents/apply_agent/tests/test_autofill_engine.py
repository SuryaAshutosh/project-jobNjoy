"""
Unit tests for AutofillEngine
"""

import pytest
from unittest.mock import Mock, AsyncMock
from ..autofill_engine import AutofillEngine

@pytest.fixture
def autofill_engine():
    """Create an AutofillEngine instance for testing"""
    return AutofillEngine()

@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing"""
    return {
        "name": "John Doe",
        "emails": ["john.doe@example.com"],
        "phones": ["+1-555-123-4567"],
        "locations": ["San Francisco, CA"],
        "experiences": [
            {
                "company": "Tech Corp",
                "title": "Senior Software Engineer",
                "bullets": ["Led development team", "Built scalable systems"]
            }
        ],
        "skills": [
            {"skill": "Python", "confidence": 0.9},
            {"skill": "React", "confidence": 0.8}
        ],
        "summary": "Experienced software engineer with 5+ years in web development"
    }

def test_get_name_value(autofill_engine, sample_resume_data):
    """Test name value extraction"""
    name = autofill_engine._get_name_value(sample_resume_data)
    assert name == "John Doe"

def test_get_email_value(autofill_engine, sample_resume_data):
    """Test email value extraction"""
    email = autofill_engine._get_email_value(sample_resume_data)
    assert email == "john.doe@example.com"

def test_get_phone_value(autofill_engine, sample_resume_data):
    """Test phone value extraction"""
    phone = autofill_engine._get_phone_value(sample_resume_data)
    assert phone == "+1-555-123-4567"

def test_get_location_value(autofill_engine, sample_resume_data):
    """Test location value extraction"""
    location = autofill_engine._get_location_value(sample_resume_data)
    assert location == "San Francisco, CA"

def test_get_current_company_value(autofill_engine, sample_resume_data):
    """Test current company value extraction"""
    company = autofill_engine._get_current_company_value(sample_resume_data)
    assert company == "Tech Corp"

def test_get_current_title_value(autofill_engine, sample_resume_data):
    """Test current title value extraction"""
    title = autofill_engine._get_current_title_value(sample_resume_data)
    assert title == "Senior Software Engineer"

def test_get_skills_value(autofill_engine, sample_resume_data):
    """Test skills value extraction"""
    skills = autofill_engine._get_skills_value(sample_resume_data)
    assert skills == "Python, React"
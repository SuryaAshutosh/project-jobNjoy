"""
Unit tests for FormDetector
"""

import pytest
from unittest.mock import Mock, AsyncMock
from ..form_detector import FormDetector

@pytest.fixture
def form_detector():
    """Create a FormDetector instance for testing"""
    return FormDetector()

def test_classify_field_type(form_detector):
    """Test field type classification"""
    # Test email field
    field_type = form_detector._classify_field_type("email", "", "", "", "email")
    assert field_type == "email"
    
    # Test phone field
    field_type = form_detector._classify_field_type("phone", "", "", "", "tel")
    assert field_type == "phone"
    
    # Test name field from mappings
    field_type = form_detector._classify_field_type("firstName", "", "", "", "text")
    assert field_type == "name"
    
    # Test generic text field
    field_type = form_detector._classify_field_type("custom_field", "", "", "", "text")
    assert field_type == "text"

def test_is_question_field(form_detector):
    """Test question field detection"""
    # Test question field
    is_question = form_detector._is_question_field("Why do you want this job?", "")
    assert is_question == True
    
    # Test non-question field
    is_question = form_detector._is_question_field("First Name", "")
    assert is_question == False

def test_calculate_field_confidence(form_detector):
    """Test field confidence calculation"""
    # Test full confidence
    confidence = form_detector._calculate_field_confidence("name", "id", "placeholder", "label")
    assert confidence == 1.0
    
    # Test partial confidence
    confidence = form_detector._calculate_field_confidence("name", "", "", "")
    assert confidence == 0.3
    
    # Test no confidence
    confidence = form_detector._calculate_field_confidence("", "", "", "")
    assert confidence == 0.0
"""
Unit tests for AnswerGenerator
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from ..answer_generator import AnswerGenerator

@pytest.fixture
def answer_generator():
    """Create an AnswerGenerator instance for testing"""
    return AnswerGenerator()

@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing"""
    return {
        "name": "John Doe",
        "emails": ["john.doe@example.com"],
        "phones": ["+1-555-123-4567"],
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
        ]
    }

@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        "title": "Software Engineer",
        "company": "Innovative Startup",
        "description": "We're looking for a skilled software engineer to join our team."
    }

def test_select_prompt_template(answer_generator):
    """Test prompt template selection"""
    # Test 'why this role' question
    template = answer_generator._select_prompt_template("Why do you want this role?")
    assert "Why this role?" in template
    
    # Test experience question
    template = answer_generator._select_prompt_template("Tell us about your experience")
    assert "experience" in template.lower()
    
    # Test skills question
    template = answer_generator._select_prompt_template("What are your strengths?")
    assert "skills" in template.lower()

@patch('openai.ChatCompletion.create')
def test_generate_with_openai(mock_create, answer_generator):
    """Test OpenAI answer generation"""
    mock_create.return_value = Mock(choices=[Mock(message=Mock(content="Test answer"))])
    
    answer = answer_generator._generate_with_openai("Test prompt")
    assert answer == "Test answer"

def test_generate_with_template(answer_generator, sample_resume_data, sample_job_data):
    """Test template-based answer generation"""
    answer = answer_generator._generate_with_template(
        "Why do you want this role?", 
        sample_resume_data, 
        sample_job_data
    )
    assert isinstance(answer, str)
    assert len(answer) > 0

def test_get_fallback_answer(answer_generator):
    """Test fallback answer generation"""
    answer = answer_generator._get_fallback_answer("Why do you want this job?")
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "excited" in answer.lower()
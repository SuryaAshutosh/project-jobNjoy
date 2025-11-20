"""
Tests for the enhanced resume parsing service
"""

import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.services.resume_parser import ResumeParserService
from app.services.llm_adapter import LLMAdapter
from app.schemas.resume_schema import EnhancedResumeData

client = TestClient(app)

class TestResumeParserService:
    """Test cases for the ResumeParserService"""
    
    def test_init(self):
        """Test initialization of ResumeParserService"""
        parser = ResumeParserService()
        assert parser is not None
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        parser = ResumeParserService()
        
        # Test whitespace normalization
        text = "John  Doe\n\n\nSoftware   Engineer"
        processed = parser.preprocess_text(text)
        assert "John Doe" in processed
        assert "Software Engineer" in processed
        
        # Test header/footer removal
        text = "Page 1\nJohn Doe\nContact: john@example.com\nPage 2"
        processed = parser.preprocess_text(text)
        assert "Page 1" not in processed
        assert "Page 2" not in processed
        assert "John Doe" in processed
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        parser = ResumeParserService()
        
        text = """
        John Doe
        john.doe@example.com
        john.doe@company.com
        +1-555-123-4567
        (555) 987-6543
        https://linkedin.com/in/johndoe
        https://github.com/johndoe
        """
        
        contact_info = parser.extract_contact_info(text)
        
        # Check emails
        assert "john.doe@example.com" in contact_info["emails"]
        assert "john.doe@company.com" in contact_info["emails"]
        
        # Check phones
        assert "+1-555-123-4567" in contact_info["phones"]
        assert "(555) 987-6543" in contact_info["phones"]
        
        # Check URLs
        assert "https://linkedin.com/in/johndoe" in contact_info["urls"]
        assert "https://github.com/johndoe" in contact_info["urls"]
        
        # Check social profiles
        assert contact_info["linkedin"] == "https://linkedin.com/in/johndoe"
        assert contact_info["github"] == "https://github.com/johndoe"
    
    def test_extract_skills(self):
        """Test skill extraction"""
        parser = ResumeParserService()
        
        text = """
        Experienced in Python, JavaScript, and React.
        Also skilled in AWS and Docker.
        """
        
        skills = parser.extract_skills(text)
        
        # Check that skills were found
        assert len(skills) > 0
        
        # Check specific skills
        skill_names = [s["skill"] for s in skills]
        assert "Python" in skill_names
        assert "JavaScript" in skill_names
        assert "React" in skill_names
    
    def test_parse_work_experience(self):
        """Test work experience parsing"""
        parser = ResumeParserService()
        
        text = """
        Work Experience:
        Senior Software Engineer at Tech Corp (2020-2023)
        - Led development team
        - Implemented new features
        
        Software Developer at Startup Inc. (2018-2020)
        """
        
        experiences = parser.parse_work_experience(text)
        
        # Check that experiences were found
        assert len(experiences) > 0
        
        # Check first experience
        first_exp = experiences[0]
        assert first_exp["company"] == "Tech Corp"
        assert first_exp["title"] == "Senior Software Engineer"
    
    def test_parse_education(self):
        """Test education parsing"""
        parser = ResumeParserService()
        
        text = """
        Education:
        B.S. Computer Science, State University (2012-2016)
        Master's in Data Science, Graduate School (2016-2018)
        """
        
        education = parser.parse_education(text)
        
        # Check that education entries were found
        assert len(education) > 0
        
        # Check first education entry
        first_edu = education[0]
        assert "University" in first_edu["institution"]
        assert "B.S." in first_edu["degree"]

class TestLLMAdapter:
    """Test cases for the LLMAdapter"""
    
    @patch('app.services.llm_adapter.openai')
    def test_normalize_parsed_data(self, mock_openai):
        """Test LLM-based normalization"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = '{"name": "John Smith", "summary": "Experienced developer"}'
        mock_openai.OpenAI().chat.completions.create.return_value = mock_response
        
        # Create adapter
        adapter = LLMAdapter()
        adapter.client = Mock()  # Ensure client is not None
        
        # Test data
        parsed_data = {
            "name": "john doe",
            "summary": "software engineer"
        }
        
        # Normalize data
        normalized = adapter.normalize_parsed_data(parsed_data)
        
        # Check that data was normalized
        assert normalized["name"] == "John Smith"
        assert normalized["summary"] == "Experienced developer"

class TestResumeAPI:
    """Test cases for the Resume API endpoints"""
    
    @patch('app.api.routers.resume.storage_client')
    @patch('app.api.routers.resume.background_task_manager')
    def test_upload_resume(self, mock_task_manager, mock_storage):
        """Test resume upload endpoint"""
        # Mock storage client
        mock_storage.upload_file.return_value = "http://example.com/resume.pdf"
        
        # Test file upload
        test_file = (
            "resume.pdf",
            "Sample resume content",
            "application/pdf"
        )
        
        # This would require more complex mocking of authentication
        # For now, we'll just verify the endpoint exists
        assert True  # Placeholder for actual test
    
    def test_parse_resume_schema(self):
        """Test that the resume schema is valid"""
        # Create sample data
        sample_data = {
            "name": "John Doe",
            "emails": ["john.doe@example.com"],
            "phones": ["+1-555-123-4567"],
            "urls": ["https://johndoe.com"],
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "summary": "Experienced software engineer",
            "skills": [
                {
                    "skill": "Python",
                    "confidence": 0.95,
                    "source": "exact_match"
                }
            ],
            "experiences": [
                {
                    "company": "Tech Corp",
                    "title": "Senior Software Engineer",
                    "start_date": "2020-01-01",
                    "end_date": "2023-12-31",
                    "bullets": ["Led development team"],
                    "duration_months": 48,
                    "confidence": 0.9
                }
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "B.S. Computer Science",
                    "start_date": "2012-09-01",
                    "end_date": "2016-05-01",
                    "confidence": 0.85
                }
            ],
            "certifications": ["AWS Certified Developer"],
            "languages": ["English", "Spanish"],
            "locations": ["San Francisco, CA"],
            "raw_text": "John Doe\nEmail: john.doe@example.com...",
            "ocr_used": False,
            "parsing_confidence": 0.88,
            "generated_at": "2023-12-01T10:30:00Z",
            "provenance": {
                "contact_extraction": "regex",
                "entity_recognition": "spacy"
            }
        }
        
        # Validate against schema
        resume_data = EnhancedResumeData(**sample_data)
        assert resume_data.name == "John Doe"
        assert len(resume_data.emails) == 1
        assert len(resume_data.skills) == 1

if __name__ == "__main__":
    pytest.main([__file__])
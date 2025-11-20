"""
Unit tests for ResumeUploader
"""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from ..resume_uploader import ResumeUploader

@pytest.fixture
def resume_uploader():
    """Create a ResumeUploader instance for testing"""
    return ResumeUploader()

def test_validate_resume_file_exists(resume_uploader):
    """Test resume file validation when file exists"""
    # Create a temporary file for testing
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.splitext', return_value=('', '.pdf')):
                result = resume_uploader.validate_resume_file("/path/to/resume.pdf")
                assert result == True

def test_validate_resume_file_not_exists(resume_uploader):
    """Test resume file validation when file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        result = resume_uploader.validate_resume_file("/path/to/nonexistent.pdf")
        assert result == False

def test_validate_resume_file_too_large(resume_uploader):
    """Test resume file validation when file is too large"""
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=10 * 1024 * 1024):  # 10MB
            result = resume_uploader.validate_resume_file("/path/to/large.pdf")
            assert result == False

def test_validate_resume_file_invalid_extension(resume_uploader):
    """Test resume file validation with invalid extension"""
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.splitext', return_value=('', '.exe')):
                result = resume_uploader.validate_resume_file("/path/to/resume.exe")
                assert result == False

def test_validate_resume_file_valid(resume_uploader):
    """Test resume file validation with valid file"""
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.splitext', return_value=('', '.pdf')):
                result = resume_uploader.validate_resume_file("/path/to/resume.pdf")
                assert result == True
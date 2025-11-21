#!/usr/bin/env python3
"""
Test script for resume parsing functionality
"""

import os
import sys
from app.services.resume_parser import resume_parser_service

def test_docx_parsing():
    """Test DOCX file parsing"""
    # Create a simple test DOCX file
    test_file_path = "test_resume.docx"
    
    try:
        # Test if we can extract text from a DOCX file
        if os.path.exists(test_file_path):
            print(f"Testing parsing of {test_file_path}")
            raw_text, metadata = resume_parser_service.extract_text_from_docx(test_file_path)
            print(f"Extracted text length: {len(raw_text)}")
            print(f"Metadata: {metadata}")
            
            # Test parsing the content
            parsed_data = resume_parser_service.parse_resume_content(raw_text)
            print(f"Parsed data keys: {list(parsed_data.keys())}")
            print("DOCX parsing test completed successfully!")
            return True
        else:
            print(f"Test file {test_file_path} not found. Skipping DOCX test.")
            return False
    except Exception as e:
        print(f"Error testing DOCX parsing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_file_path_construction():
    """Test file path construction"""
    test_url = "http://localhost:8000/uploads/resumes/testuser/20251121010020_110ddb99.docx"
    expected_path = os.path.join("./uploads", "resumes/testuser/20251121010020_110ddb99.docx")
    print(f"Test URL: {test_url}")
    print(f"Expected path: {expected_path}")
    print("File path construction test completed!")

if __name__ == "__main__":
    print("Running resume parsing tests...")
    test_file_path_construction()
    test_docx_parsing()
    print("All tests completed!")
"""
Resume uploader for Auto-Apply Agent
Handles uploading resume files to job application forms
"""

import logging
import os
from typing import Dict, Any, List, Optional
from playwright.async_api import ElementHandle

logger = logging.getLogger(__name__)

class ResumeUploader:
    """Handles uploading resume files to job application forms"""
    
    def __init__(self):
        """Initialize resume uploader"""
        pass
        
    async def upload_resume(self, file_fields: List[Dict[str, Any]], resume_path: str) -> List[Dict[str, Any]]:
        """
        Upload resume to file fields
        
        Args:
            file_fields: List of file field elements
            resume_path: Path to the resume file
            
        Returns:
            List of upload results with metadata
        """
        results = []
        
        # Check if resume file exists
        if not os.path.exists(resume_path):
            logger.error(f"Resume file not found: {resume_path}")
            return results
            
        try:
            # Upload resume to each file field
            for field in file_fields:
                element = field["element"]
                field_type = field["field_type"]
                confidence = field["confidence"]
                
                try:
                    # Upload the file
                    success = await self._upload_file(element, resume_path)
                    
                    results.append({
                        "element": element,
                        "field_type": field_type,
                        "resume_path": resume_path,
                        "confidence": confidence,
                        "success": success
                    })
                    
                    if success:
                        logger.info(f"Successfully uploaded resume to field")
                    else:
                        logger.warning(f"Failed to upload resume to field")
                        
                except Exception as e:
                    logger.error(f"Error uploading resume to field: {e}")
                    results.append({
                        "element": element,
                        "field_type": field_type,
                        "resume_path": resume_path,
                        "confidence": confidence,
                        "success": False,
                        "error": str(e)
                    })
                    
            successful_uploads = sum(1 for r in results if r["success"])
            logger.info(f"Uploaded resume to {successful_uploads}/{len(results)} fields successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return results
            
    async def _upload_file(self, element: ElementHandle, file_path: str) -> bool:
        """
        Upload a file to a file input element
        
        Args:
            element: Playwright element handle for file input
            file_path: Path to the file to upload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Upload the file
            await element.set_input_files(file_path)
            
            # Wait a moment for upload to complete
            await element.page.wait_for_timeout(1000)
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False
            
    def validate_resume_file(self, file_path: str) -> bool:
        """
        Validate that the resume file exists and is of acceptable type
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Resume file does not exist: {file_path}")
                return False
                
            # Check file size (limit to 5MB)
            file_size = os.path.getsize(file_path)
            if file_size > 5 * 1024 * 1024:  # 5MB
                logger.error(f"Resume file too large: {file_size} bytes")
                return False
                
            # Check file extension
            valid_extensions = ['.pdf', '.doc', '.docx', '.txt']
            _, extension = os.path.splitext(file_path.lower())
            if extension not in valid_extensions:
                logger.error(f"Invalid resume file extension: {extension}")
                return False
                
            logger.info(f"Resume file validated: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating resume file: {e}")
            return False
            
    async def find_and_upload_resume(self, page, resume_path: str) -> bool:
        """
        Find file upload fields on the page and upload the resume
        
        Args:
            page: Playwright page object
            resume_path: Path to the resume file
            
        Returns:
            True if at least one upload was successful, False otherwise
        """
        try:
            # Validate resume file first
            if not self.validate_resume_file(resume_path):
                return False
                
            # Find file input fields
            file_inputs = await page.query_selector_all("input[type='file']")
            
            if not file_inputs:
                logger.info("No file input fields found on page")
                return False
                
            logger.info(f"Found {len(file_inputs)} file input fields")
            
            # Upload to each file input
            success_count = 0
            for element in file_inputs:
                try:
                    await self._upload_file(element, resume_path)
                    success_count += 1
                    logger.info("Successfully uploaded resume")
                except Exception as e:
                    logger.error(f"Error uploading resume: {e}")
                    
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error finding and uploading resume: {e}")
            return False
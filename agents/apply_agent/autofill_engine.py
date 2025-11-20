"""
Autofill engine for Auto-Apply Agent
Intelligently fills form fields using parsed resume data
"""

import logging
import re
from typing import Dict, Any, List, Optional
from playwright.async_api import ElementHandle
from .utils.settings import settings

logger = logging.getLogger(__name__)

class AutofillEngine:
    """Intelligently fills form fields using parsed resume data"""
    
    def __init__(self):
        """Initialize autofill engine"""
        self.field_mappings = settings.get("field_mappings", {})
        
    def map_resume_to_fields(self, resume_data: Dict[str, Any], form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map resume data to form fields
        
        Args:
            resume_data: Parsed resume data
            form_fields: Detected form fields
            
        Returns:
            Dictionary mapping field elements to values
        """
        field_mapping = {}
        
        try:
            # Process each form field
            for field in form_fields:
                element = field["element"]
                field_type = field["field_type"]
                confidence = field["confidence"]
                
                # Get value for this field type
                value = self._get_value_for_field(field_type, resume_data, field)
                
                if value:
                    field_mapping[element] = {
                        "value": value,
                        "field_type": field_type,
                        "confidence": confidence,
                        "source_field": field
                    }
                    
            logger.info(f"Mapped values to {len(field_mapping)} fields")
            return field_mapping
            
        except Exception as e:
            logger.error(f"Error mapping resume to fields: {e}")
            return field_mapping
            
    def _get_value_for_field(self, field_type: str, resume_data: Dict[str, Any], field: Dict[str, Any]) -> Optional[str]:
        """
        Get appropriate value for a field type from resume data
        
        Args:
            field_type: Type of field to fill
            resume_data: Parsed resume data
            field: Field metadata
            
        Returns:
            Value to fill in the field or None
        """
        try:
            # Handle specific field types
            if field_type == "name":
                return self._get_name_value(resume_data)
            elif field_type == "email":
                return self._get_email_value(resume_data)
            elif field_type == "phone":
                return self._get_phone_value(resume_data)
            elif field_type == "location":
                return self._get_location_value(resume_data)
            elif field_type == "current_company":
                return self._get_current_company_value(resume_data)
            elif field_type == "current_title":
                return self._get_current_title_value(resume_data)
            elif field_type == "skills":
                return self._get_skills_value(resume_data)
            elif field_type == "salary_expectations":
                return self._get_salary_expectations_value(resume_data)
            elif field_type == "file":
                return self._get_file_value(resume_data)
            elif field_type == "question":
                # Questions are handled by the answer generator
                return None
            elif field_type == "textarea":
                # Textareas might be questions or other fields
                return self._get_textarea_value(resume_data, field)
            else:
                # Generic text field
                return self._get_generic_text_value(resume_data, field)
                
        except Exception as e:
            logger.warning(f"Error getting value for field type {field_type}: {e}")
            return None
            
    def _get_name_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get name value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Name value or None
        """
        # Try to get name from different sources
        name = resume_data.get("name", "")
        if name:
            return name
            
        # Try to construct from first and last name
        first_name = ""
        last_name = ""
        
        # Look in experiences for current position
        experiences = resume_data.get("experiences", [])
        if experiences:
            current_exp = experiences[0]  # Assume first experience is most recent
            # This is a simplification - in reality, we'd need better logic
            name_parts = current_exp.get("company", "").split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
                
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
            
        return None
        
    def _get_email_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get email value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Email value or None
        """
        emails = resume_data.get("emails", [])
        if emails:
            return emails[0]  # Return first email
        return None
        
    def _get_phone_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get phone value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Phone value or None
        """
        phones = resume_data.get("phones", [])
        if phones:
            return phones[0]  # Return first phone
        return None
        
    def _get_location_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get location value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Location value or None
        """
        locations = resume_data.get("locations", [])
        if locations:
            return locations[0]  # Return first location
        return None
        
    def _get_current_company_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get current company value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Current company value or None
        """
        experiences = resume_data.get("experiences", [])
        if experiences:
            current_exp = experiences[0]  # Assume first experience is most recent
            return current_exp.get("company", "")
        return None
        
    def _get_current_title_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get current title value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Current title value or None
        """
        experiences = resume_data.get("experiences", [])
        if experiences:
            current_exp = experiences[0]  # Assume first experience is most recent
            return current_exp.get("title", "")
        return None
        
    def _get_skills_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get skills value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Skills value or None
        """
        skills = resume_data.get("skills", [])
        if skills:
            # Return comma-separated list of skill names
            skill_names = [skill.get("skill", "") for skill in skills if skill.get("skill")]
            return ", ".join(skill_names)
        return None
        
    def _get_salary_expectations_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get salary expectations value (placeholder implementation)
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Salary expectations value or None
        """
        # This would typically come from user input or be calculated
        # For now, we'll return None to indicate it should be handled separately
        return None
        
    def _get_file_value(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """
        Get file path value from resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            File path value or None
        """
        # This would be the path to the resume file
        # In a real implementation, this would be configurable
        return "/path/to/resume.pdf"  # Placeholder
        
    def _get_textarea_value(self, resume_data: Dict[str, Any], field: Dict[str, Any]) -> Optional[str]:
        """
        Get textarea value (might be a question or other field)
        
        Args:
            resume_data: Parsed resume data
            field: Field metadata
            
        Returns:
            Textarea value or None
        """
        # For now, we'll treat textareas as questions to be handled by the answer generator
        # In a real implementation, we might have more sophisticated logic
        return None
        
    def _get_generic_text_value(self, resume_data: Dict[str, Any], field: Dict[str, Any]) -> Optional[str]:
        """
        Get generic text value for fields that don't match specific types
        
        Args:
            resume_data: Parsed resume data
            field: Field metadata
            
        Returns:
            Generic text value or None
        """
        # Try to match field name/label against resume data
        field_name = field.get("name", "").lower()
        field_id = field.get("id", "").lower()
        field_label = field.get("label", "").lower()
        field_placeholder = field.get("placeholder", "").lower()
        
        combined_text = f"{field_name} {field_id} {field_label} {field_placeholder}"
        
        # Look for matches in resume data
        if "summary" in combined_text and resume_data.get("summary"):
            return resume_data.get("summary")
            
        # If no specific match, return None to indicate it should be handled separately
        return None
        
    async def fill_fields(self, field_mapping: Dict[ElementHandle, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fill form fields with mapped values
        
        Args:
            field_mapping: Dictionary mapping field elements to values
            
        Returns:
            List of fill results with metadata
        """
        results = []
        
        try:
            for element, field_data in field_mapping.items():
                try:
                    value = field_data["value"]
                    field_type = field_data["field_type"]
                    confidence = field_data["confidence"]
                    
                    # Fill the field
                    success = await self._fill_field(element, value, field_type)
                    
                    results.append({
                        "element": element,
                        "field_type": field_type,
                        "value": value,
                        "confidence": confidence,
                        "success": success
                    })
                    
                    if success:
                        logger.info(f"Successfully filled {field_type} field")
                    else:
                        logger.warning(f"Failed to fill {field_type} field")
                        
                except Exception as e:
                    logger.error(f"Error filling field {field_data.get('field_type', 'unknown')}: {e}")
                    results.append({
                        "element": element,
                        "field_type": field_data.get("field_type", "unknown"),
                        "value": field_data.get("value", ""),
                        "confidence": field_data.get("confidence", 0.0),
                        "success": False,
                        "error": str(e)
                    })
                    
            successful_fills = sum(1 for r in results if r["success"])
            logger.info(f"Filled {successful_fills}/{len(results)} fields successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error filling fields: {e}")
            return results
            
    async def _fill_field(self, element: ElementHandle, value: str, field_type: str) -> bool:
        """
        Fill a single field with a value
        
        Args:
            element: Playwright element handle
            value: Value to fill
            field_type: Type of field
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle different field types
            if field_type == "file":
                # For file fields, we need to upload a file
                # This is a placeholder - in reality, we'd need the actual file path
                # await element.set_input_files(value)
                logger.info(f"Would upload file: {value}")
                return True
            else:
                # For text fields, fill the value
                await element.fill(value)
                
                # Trigger any onChange events
                await element.press("Tab")
                
                return True
                
        except Exception as e:
            logger.warning(f"Error filling field: {e}")
            return False
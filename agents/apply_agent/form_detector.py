"""
Form detector for Auto-Apply Agent
Detects and analyzes form elements on job application pages
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import Page, ElementHandle
from .utils.settings import settings

logger = logging.getLogger(__name__)

class FormDetector:
    """Detects and analyzes form elements on job application pages"""
    
    def __init__(self):
        """Initialize form detector"""
        self.field_mappings = settings.get("field_mappings", {})
        
    async def detect_form_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect all form fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected form fields with metadata
        """
        fields = []
        
        try:
            # Detect input fields
            input_fields = await self._detect_input_fields(page)
            fields.extend(input_fields)
            
            # Detect textarea fields
            textarea_fields = await self._detect_textarea_fields(page)
            fields.extend(textarea_fields)
            
            # Detect select fields
            select_fields = await self._detect_select_fields(page)
            fields.extend(select_fields)
            
            # Detect file upload fields
            file_fields = await self._detect_file_fields(page)
            fields.extend(file_fields)
            
            logger.info(f"Detected {len(fields)} form fields")
            return fields
            
        except Exception as e:
            logger.error(f"Error detecting form fields: {e}")
            return fields
            
    async def _detect_input_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect input fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected input fields
        """
        fields = []
        
        try:
            # Common input selectors
            input_selectors = [
                "input[type='text']",
                "input[type='email']",
                "input[type='tel']",
                "input[type='number']",
                "input[type='date']",
                "input:not([type])",  # Inputs without type attribute default to text
                "input[type='password']"
            ]
            
            for selector in input_selectors:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    field = await self._analyze_input_field(element, page)
                    if field:
                        fields.append(field)
                        
        except Exception as e:
            logger.error(f"Error detecting input fields: {e}")
            
        return fields
        
    async def _detect_textarea_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect textarea fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected textarea fields
        """
        fields = []
        
        try:
            elements = await page.query_selector_all("textarea")
            for element in elements:
                field = await self._analyze_textarea_field(element, page)
                if field:
                    fields.append(field)
                    
        except Exception as e:
            logger.error(f"Error detecting textarea fields: {e}")
            
        return fields
        
    async def _detect_select_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect select fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected select fields
        """
        fields = []
        
        try:
            elements = await page.query_selector_all("select")
            for element in elements:
                field = await self._analyze_select_field(element, page)
                if field:
                    fields.append(field)
                    
        except Exception as e:
            logger.error(f"Error detecting select fields: {e}")
            
        return fields
        
    async def _detect_file_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect file upload fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected file fields
        """
        fields = []
        
        try:
            elements = await page.query_selector_all("input[type='file']")
            for element in elements:
                field = await self._analyze_file_field(element, page)
                if field:
                    fields.append(field)
                    
        except Exception as e:
            logger.error(f"Error detecting file fields: {e}")
            
        return fields
        
    async def _analyze_input_field(self, element: ElementHandle, page: Page) -> Optional[Dict[str, Any]]:
        """
        Analyze an input field and extract metadata
        
        Args:
            element: Playwright element handle
            page: Playwright page object
            
        Returns:
            Dictionary with field metadata or None if analysis fails
        """
        try:
            # Get element attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            input_type = await element.get_attribute("type") or "text"
            name = await element.get_attribute("name") or ""
            id_attr = await element.get_attribute("id") or ""
            placeholder = await element.get_attribute("placeholder") or ""
            label_text = await self._get_associated_label_text(element, page)
            
            # Determine field type based on attributes and label
            field_type = self._classify_field_type(name, id_attr, placeholder, label_text, input_type)
            
            return {
                "element": element,
                "tag": tag_name,
                "type": input_type,
                "field_type": field_type,
                "name": name,
                "id": id_attr,
                "placeholder": placeholder,
                "label": label_text,
                "confidence": self._calculate_field_confidence(name, id_attr, placeholder, label_text)
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing input field: {e}")
            return None
            
    async def _analyze_textarea_field(self, element: ElementHandle, page: Page) -> Optional[Dict[str, Any]]:
        """
        Analyze a textarea field and extract metadata
        
        Args:
            element: Playwright element handle
            page: Playwright page object
            
        Returns:
            Dictionary with field metadata or None if analysis fails
        """
        try:
            # Get element attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            name = await element.get_attribute("name") or ""
            id_attr = await element.get_attribute("id") or ""
            placeholder = await element.get_attribute("placeholder") or ""
            label_text = await self._get_associated_label_text(element, page)
            
            # Textareas are typically for longer text input
            field_type = "textarea"
            
            # Check if it's a question field
            if self._is_question_field(label_text, placeholder):
                field_type = "question"
                
            return {
                "element": element,
                "tag": tag_name,
                "type": "textarea",
                "field_type": field_type,
                "name": name,
                "id": id_attr,
                "placeholder": placeholder,
                "label": label_text,
                "confidence": self._calculate_field_confidence(name, id_attr, placeholder, label_text)
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing textarea field: {e}")
            return None
            
    async def _analyze_select_field(self, element: ElementHandle, page: Page) -> Optional[Dict[str, Any]]:
        """
        Analyze a select field and extract metadata
        
        Args:
            element: Playwright element handle
            page: Playwright page object
            
        Returns:
            Dictionary with field metadata or None if analysis fails
        """
        try:
            # Get element attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            name = await element.get_attribute("name") or ""
            id_attr = await element.get_attribute("id") or ""
            label_text = await self._get_associated_label_text(element, page)
            
            # Select fields are typically for choice selection
            field_type = "select"
            
            return {
                "element": element,
                "tag": tag_name,
                "type": "select",
                "field_type": field_type,
                "name": name,
                "id": id_attr,
                "placeholder": "",
                "label": label_text,
                "confidence": self._calculate_field_confidence(name, id_attr, "", label_text)
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing select field: {e}")
            return None
            
    async def _analyze_file_field(self, element: ElementHandle, page: Page) -> Optional[Dict[str, Any]]:
        """
        Analyze a file field and extract metadata
        
        Args:
            element: Playwright element handle
            page: Playwright page object
            
        Returns:
            Dictionary with field metadata or None if analysis fails
        """
        try:
            # Get element attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            name = await element.get_attribute("name") or ""
            id_attr = await element.get_attribute("id") or ""
            label_text = await self._get_associated_label_text(element, page)
            
            # File fields are for resume/CV uploads
            field_type = "file"
            
            return {
                "element": element,
                "tag": tag_name,
                "type": "file",
                "field_type": field_type,
                "name": name,
                "id": id_attr,
                "placeholder": "",
                "label": label_text,
                "confidence": self._calculate_field_confidence(name, id_attr, "", label_text)
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing file field: {e}")
            return None
            
    async def _get_associated_label_text(self, element: ElementHandle, page: Page) -> str:
        """
        Get text from associated label element
        
        Args:
            element: Playwright element handle
            page: Playwright page object
            
        Returns:
            Label text or empty string
        """
        try:
            # Try to get label by "for" attribute
            element_id = await element.get_attribute("id")
            if element_id:
                label = await page.query_selector(f"label[for='{element_id}']")
                if label:
                    return await label.text_content() or ""
                    
            # Try to get parent label
            parent = await element.evaluate_handle("el => el.closest('label')")
            if parent:
                return await parent.text_content() or ""
                
            # Try to get adjacent label
            label = await element.evaluate_handle("el => el.previousElementSibling")
            if label:
                tag_name = await label.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "label":
                    return await label.text_content() or ""
                    
        except Exception as e:
            logger.warning(f"Error getting associated label text: {e}")
            
        return ""
        
    def _classify_field_type(self, name: str, id_attr: str, placeholder: str, label_text: str, input_type: str) -> str:
        """
        Classify field type based on attributes and text
        
        Args:
            name: Field name attribute
            id_attr: Field id attribute
            placeholder: Field placeholder text
            label_text: Associated label text
            input_type: Input type attribute
            
        Returns:
            Classified field type
        """
        # Combine all text for matching
        combined_text = f"{name} {id_attr} {placeholder} {label_text}".lower()
        
        # Check for specific field types
        if input_type == "email":
            return "email"
        elif input_type == "tel":
            return "phone"
        elif input_type == "file":
            return "file"
            
        # Check field mappings
        for field_type, keywords in self.field_mappings.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    return field_type
                    
        # Default to generic text field
        return "text"
        
    def _is_question_field(self, label_text: str, placeholder: str) -> bool:
        """
        Determine if a field is a question field based on text content
        
        Args:
            label_text: Label text
            placeholder: Placeholder text
            
        Returns:
            True if field is a question field
        """
        question_keywords = [
            "why", "describe", "experience", "qualification", "skill", 
            "strength", "weakness", "challenge", "achievement", "motivation",
            "interest", "background", "fit", "contribute", "goal"
        ]
        
        combined_text = f"{label_text} {placeholder}".lower()
        
        for keyword in question_keywords:
            if keyword in combined_text:
                return True
                
        return False
        
    def _calculate_field_confidence(self, name: str, id_attr: str, placeholder: str, label_text: str) -> float:
        """
        Calculate confidence score for field detection
        
        Args:
            name: Field name attribute
            id_attr: Field id attribute
            placeholder: Field placeholder text
            label_text: Associated label text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Weight different attributes
        if name:
            score += 0.3
        if id_attr:
            score += 0.2
        if placeholder:
            score += 0.25
        if label_text:
            score += 0.25
            
        return round(min(score, 1.0), 2)
        
    async def detect_questions(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect open-ended question fields on the page
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected question fields
        """
        questions = []
        
        try:
            # Get all form fields
            fields = await self.detect_form_fields(page)
            
            # Filter for question fields (textareas and specific input fields)
            for field in fields:
                if field["field_type"] == "question" or field["field_type"] == "textarea":
                    # Extract question text
                    question_text = field["label"] or field["placeholder"] or ""
                    
                    if question_text:
                        questions.append({
                            "element": field["element"],
                            "question_text": question_text,
                            "field_type": field["field_type"],
                            "confidence": field["confidence"]
                        })
                        
            # Also look for div-based questions
            div_questions = await self._detect_div_questions(page)
            questions.extend(div_questions)
            
            logger.info(f"Detected {len(questions)} question fields")
            return questions
            
        except Exception as e:
            logger.error(f"Error detecting questions: {e}")
            return questions
            
    async def _detect_div_questions(self, page: Page) -> List[Dict[str, Any]]:
        """
        Detect question fields that are in div elements
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected div-based question fields
        """
        questions = []
        
        try:
            # Look for common question container patterns
            question_selectors = [
                "div:has-text('Why')",
                "div:has-text('Describe')",
                "div:has-text('Experience')",
                "div:has-text('Tell us')",
                "div[class*='question']",
                "div[class*='prompt']",
                "div[data-question]",
                "div[aria-label*='question' i]"
            ]
            
            for selector in question_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        # Get the text content
                        text_content = await element.text_content() or ""
                        
                        # Check if it looks like a question
                        if self._is_question_text(text_content):
                            # Look for associated input/textarea
                            input_element = await element.query_selector("input, textarea")
                            if input_element:
                                questions.append({
                                    "element": input_element,
                                    "question_text": text_content.strip(),
                                    "field_type": "div_question",
                                    "confidence": 0.8
                                })
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error detecting div questions: {e}")
            
        return questions
        
    def _is_question_text(self, text: str) -> bool:
        """
        Determine if text looks like a question
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text looks like a question
        """
        if not text:
            return False
            
        text = text.lower().strip()
        
        # Check for question marks
        if "?" in text:
            return True
            
        # Check for question keywords at the beginning
        question_starters = [
            "why", "describe", "tell us", "explain", "how", "what", 
            "please", "share", "discuss", "elaborate"
        ]
        
        for starter in question_starters:
            if text.startswith(starter):
                return True
                
        return False
"""
Enhanced Resume parsing service for JobBuddy with NLP and LLM capabilities
"""

import os
import tempfile
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
from functools import wraps
import time

# Text extraction libraries
try:
    import PyPDF2
    import pdfplumber
    from docx import Document
except ImportError:
    pass

# NLP libraries
try:
    import spacy
    from spacy.matcher import PhraseMatcher
    from rapidfuzz import fuzz, process
except ImportError:
    pass

# Logging setup
logger = logging.getLogger(__name__)

# Retry decorator for transient failures
def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempts} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator

class ResumeParserService:
    """Enhanced resume parser service with modular components"""
    
    def __init__(self):
        """Initialize the parser service with configurable components"""
        self.nlp = None
        self.skill_taxonomy = {}
        self.phrase_matcher = None
        self._load_nlp_model()
        self._load_skill_taxonomy()
        
    def _load_nlp_model(self):
        """Load spaCy NLP model if available"""
        try:
            # Try loading the transformer model first (more accurate)
            try:
                self.nlp = spacy.load("en_core_web_trf")
            except OSError:
                # Fallback to smaller model
                self.nlp = spacy.load("en_core_web_sm")
            
            self.phrase_matcher = PhraseMatcher(self.nlp.vocab)
            logger.info("NLP model loaded successfully")
        except Exception as e:
            logger.warning(f"NLP model not available: {str(e)}")
            self.nlp = None
            self.phrase_matcher = None
    
    def _load_skill_taxonomy(self):
        """Load skill taxonomy from JSON file or use default"""
        try:
            # In a real implementation, this would load from a JSON file
            self.skill_taxonomy = {
                "programming_languages": [
                    "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "Swift", "Kotlin", "TypeScript"
                ],
                "web_technologies": [
                    "React", "Vue.js", "Angular", "Node.js", "Express", "Django", "Flask", "Spring Boot"
                ],
                "databases": [
                    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server"
                ],
                "cloud_platforms": [
                    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform"
                ]
            }
            logger.info("Skill taxonomy loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load skill taxonomy: {str(e)}")
            self.skill_taxonomy = {}

    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from a PDF file with OCR fallback
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        metadata = {
            "ocr_used": False,
            "confidence": 1.0,
            "pages": 0
        }
        
        try:
            # First try extracting text directly
            text = ""
            with pdfplumber.open(file_path) as pdf:
                metadata["pages"] = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If we got text, return it
            if text.strip():
                metadata["confidence"] = 0.9
                return text, metadata
                
            # If no text found, try OCR as fallback
            logger.info("No selectable text found in PDF, attempting OCR")
            text, ocr_metadata = self._extract_text_with_ocr(file_path)
            metadata.update(ocr_metadata)
            return text, metadata
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def _extract_text_with_ocr(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from PDF using OCR (fallback method)
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF
            
            text = ""
            doc = fitz.open(file_path)
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Perform OCR
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
            
            doc.close()
            
            metadata = {
                "ocr_used": True,
                "confidence": 0.7,  # Lower confidence for OCR
                "pages": doc.page_count
            }
            
            return text, metadata
            
        except ImportError:
            logger.error("OCR libraries not installed")
            raise Exception("OCR libraries (pytesseract, PyMuPDF) not installed")
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from a DOCX file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            doc = Document(file_path)
            text = ""
            
            # Extract paragraphs
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
            
            metadata = {
                "ocr_used": False,
                "confidence": 0.95,
                "paragraphs": len(doc.paragraphs)
            }
            
            return text, metadata
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from a TXT file
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            
            metadata = {
                "ocr_used": False,
                "confidence": 1.0,
                "characters": len(text)
            }
            
            return text, metadata
        except Exception as e:
            raise Exception(f"Failed to extract text from TXT: {str(e)}")

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text: normalize whitespace, remove headers/footers
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove common header/footer patterns (simplified)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like page numbers or common headers
            if re.match(r'^\s*\d+\s*$', line):  # Just a number (page number)
                continue
            if re.match(r'^\s*[Pp]age\s*\d+.*$', line):  # Page x of y
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """
        Extract contact information using regex patterns
        
        Args:
            text: Text to extract contact info from
            
        Returns:
            Dict: Extracted contact information
        """
        contact_info = {
            "emails": [],
            "phones": [],
            "urls": [],
            "linkedin": None,
            "github": None,
            "location": None
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info["emails"] = list(set(emails))  # Remove duplicates
        
        # Phone pattern (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\b\d{3}\s+\d{3}\s+\d{4}\b'       # 123 456 7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        contact_info["phones"] = list(set(phones))  # Remove duplicates
        
        # URL pattern
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        urls = re.findall(url_pattern, text)
        contact_info["urls"] = list(set(urls))  # Remove duplicates
        
        # LinkedIn profile
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
        linkedin_matches = re.findall(linkedin_pattern, text)
        if linkedin_matches:
            contact_info["linkedin"] = linkedin_matches[0]
        
        # GitHub profile
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
        github_matches = re.findall(github_pattern, text)
        if github_matches:
            contact_info["github"] = github_matches[0]
        
        return contact_info

    def extract_entities_with_spacy(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities using spaCy NLP model
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dict: Extracted entities
        """
        if not self.nlp:
            return {}
        
        try:
            doc = self.nlp(text)
            
            entities = {
                "organizations": [],
                "persons": [],
                "locations": [],
                "dates": [],
                "skills": []
            }
            
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    entities["organizations"].append(ent.text)
                elif ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
                elif ent.label_ == "GPE":  # Geopolitical entity (countries, cities, states)
                    entities["locations"].append(ent.text)
                elif ent.label_ == "DATE":
                    entities["dates"].append(ent.text)
            
            # Deduplicate entities
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
        except Exception as e:
            logger.error(f"spaCy entity extraction failed: {str(e)}")
            return {}

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract skills using taxonomy and fuzzy matching
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List[Dict]: Extracted skills with confidence scores
        """
        skills = []
        
        # Flatten skill taxonomy
        all_skills = []
        for category, skill_list in self.skill_taxonomy.items():
            all_skills.extend(skill_list)
        
        if not all_skills:
            return skills
        
        # Use fuzzy matching to find skills
        text_lower = text.lower()
        found_skills = set()
        
        for skill in all_skills:
            # Exact match
            if skill.lower() in text_lower:
                skills.append({
                    "skill": skill,
                    "confidence": 0.95,
                    "source": "exact_match"
                })
                found_skills.add(skill.lower())
                continue
            
            # Fuzzy match
            match_result = process.extractOne(skill, [text_lower], scorer=fuzz.partial_ratio)
            if match_result and match_result[1] > 80:  # 80% similarity threshold
                matched_text, score, _ = match_result
                skills.append({
                    "skill": skill,
                    "confidence": score / 100.0,
                    "source": "fuzzy_match"
                })
                found_skills.add(skill.lower())
        
        return skills

    def parse_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse work experience sections
        
        Args:
            text: Text to parse experience from
            
        Returns:
            List[Dict]: Parsed work experiences
        """
        experiences = []
        
        # Look for experience section indicators
        exp_indicators = [
            "work experience", "employment", "professional experience", 
            "career history", "job history"
        ]
        
        lines = text.split('\n')
        in_experience_section = False
        current_experience = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering an experience section
            if any(indicator in line.lower() for indicator in exp_indicators):
                in_experience_section = True
                continue
            
            # If we're in experience section, try to parse job entries
            if in_experience_section:
                # Simple heuristic: lines with company-like patterns
                if re.search(r'\b(at|@|for)\s+[A-Z][a-z]+', line):
                    if current_experience:
                        experiences.append(current_experience)
                    
                    # Parse company and position
                    parts = re.split(r'\s+(?:at|@|for)\s+', line, 1)
                    if len(parts) == 2:
                        position = parts[0].strip()
                        company = parts[1].strip()
                        
                        current_experience = {
                            "company": company,
                            "title": position,
                            "start_date": None,
                            "end_date": None,
                            "bullets": [],
                            "duration_months": None,
                            "confidence": 0.8
                        }
        
        # Add the last experience if exists
        if current_experience:
            experiences.append(current_experience)
        
        return experiences

    def parse_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse education sections
        
        Args:
            text: Text to parse education from
            
        Returns:
            List[Dict]: Parsed education entries
        """
        education = []
        
        # Look for education section indicators
        edu_indicators = [
            "education", "academic background", "degrees", "qualifications"
        ]
        
        lines = text.split('\n')
        in_education_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering an education section
            if any(indicator in line.lower() for indicator in edu_indicators):
                in_education_section = True
                continue
            
            # Simple education parsing (would be enhanced in production)
            if in_education_section and re.search(r'\b(university|college|school|degree|bs|ba|ms|ma|phd)\b', line.lower()):
                edu_entry = {
                    "institution": line,
                    "degree": None,
                    "start_date": None,
                    "end_date": None,
                    "confidence": 0.7
                }
                education.append(edu_entry)
        
        return education

    def generate_summary(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate a professional summary from parsed data
        
        Args:
            parsed_data: Parsed resume data
            
        Returns:
            str: Generated summary
        """
        # This would typically call an LLM in production
        # For now, we'll generate a simple summary
        
        experiences = parsed_data.get("experiences", [])
        skills = parsed_data.get("skills", [])
        
        if not experiences and not skills:
            return "Professional with diverse background and skills."
        
        summary_parts = []
        
        if experiences:
            latest_exp = experiences[0] if experiences else None
            if latest_exp:
                summary_parts.append(f"Experienced professional with background in {latest_exp.get('title', 'various roles')}")
        
        if skills:
            top_skills = [s["skill"] for s in skills[:3]]
            if top_skills:
                skills_str = ", ".join(top_skills)
                summary_parts.append(f"Skilled in {skills_str}")
        
        return ". ".join(summary_parts) + "." if summary_parts else "Professional summary."

    def parse_resume_content(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse resume content and extract structured data using modular pipeline
        
        Args:
            raw_text: Raw text extracted from resume
            
        Returns:
            Dict: Parsed resume data with confidence scores and provenance
        """
        # Preprocess text
        processed_text = self.preprocess_text(raw_text)
        
        # Extract contact information
        contact_info = self.extract_contact_info(processed_text)
        
        # Extract entities with spaCy
        entities = self.extract_entities_with_spacy(processed_text)
        
        # Extract skills
        skills = self.extract_skills(processed_text)
        
        # Parse work experience
        experiences = self.parse_work_experience(processed_text)
        
        # Parse education
        education = self.parse_education(processed_text)
        
        # Generate summary
        summary = self.generate_summary({
            "experiences": experiences,
            "skills": skills
        })
        
        # Combine all parsed data
        parsed_data = {
            "name": entities.get("persons", [""])[0] if entities.get("persons") else "",
            "emails": contact_info.get("emails", []),
            "phones": contact_info.get("phones", []),
            "urls": contact_info.get("urls", []),
            "linkedin": contact_info.get("linkedin"),
            "github": contact_info.get("github"),
            "summary": summary,
            "skills": skills,
            "experiences": experiences,
            "education": education,
            "certifications": [],
            "languages": [],
            "locations": entities.get("locations", []),
            "generated_at": datetime.utcnow().isoformat(),
            "parsing_confidence": 0.85,  # Overall confidence estimate
            "provenance": {
                "contact_extraction": "regex",
                "entity_recognition": "spacy" if self.nlp else "none",
                "skill_extraction": "taxonomy_matching",
                "experience_parsing": "heuristic",
                "education_parsing": "heuristic",
                "summary_generation": "template_based"
            }
        }
        
        return parsed_data

    @retry(max_attempts=3, delay=1, backoff=2)
    def process_resume_file(self, file_url: str) -> Dict[str, Any]:
        """
        Process a resume file from storage and extract structured data
        
        Args:
            file_url: URL of the resume file in storage
            
        Returns:
            Dict: Raw text, metadata and parsed data
        """
        # For local storage, we can work directly with the file
        # For S3/MinIO, we would need to download it first
    
        try:
            # Download file from storage (simplified for local storage)
            if file_url.startswith("http://localhost:8000/uploads/"):
                # Local file - construct path
                file_key = file_url.replace("http://localhost:8000/uploads/", "")
                upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
                file_path = os.path.join(upload_dir, file_key)
                
                # Log the file path for debugging
                print(f"Attempting to parse file: {file_path}")
            else:
                # S3/MinIO - download file
                # This is a simplified implementation
                # In a real implementation, you would download from S3
                raise Exception("S3 download not implemented in this simplified version")
        
            # Check if file exists
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path} (cwd: {os.getcwd()})")
        
            # Determine file type and extract text
            if file_url.lower().endswith('.pdf'):
                raw_text, metadata = self.extract_text_from_pdf(file_path)
            elif file_url.lower().endswith('.docx'):
                raw_text, metadata = self.extract_text_from_docx(file_path)
            elif file_url.lower().endswith('.txt'):
                raw_text, metadata = self.extract_text_from_txt(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_url}")
        
            # Parse the extracted text
            parsed_data = self.parse_resume_content(raw_text)
        
            # Add metadata to parsed data
            parsed_data["ocr_used"] = metadata.get("ocr_used", False)
            parsed_data["parsing_confidence"] = metadata.get("confidence", 0.85)
        
            return {
                "raw_text": raw_text,
                "metadata": metadata,
                "parsed_data": parsed_data
            }
        
        except Exception as e:
            print(f"Error processing resume file: {str(e)}")
            raise

# Global instance
resume_parser_service = ResumeParserService()
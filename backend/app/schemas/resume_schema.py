"""
Enhanced resume schema definitions for JobBuddy
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class SkillEntry(BaseModel):
    """Schema for a single skill entry"""
    skill: str = Field(..., description="The skill name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this skill extraction")
    source: str = Field(..., description="Source of the skill extraction (e.g., 'exact_match', 'fuzzy_match')")

class ExperienceEntry(BaseModel):
    """Schema for a single work experience entry"""
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: Optional[str] = Field(None, description="Start date in ISO format (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date in ISO format (YYYY-MM-DD)")
    bullets: List[str] = Field(default_factory=list, description="Bullet points describing responsibilities")
    duration_months: Optional[int] = Field(None, description="Duration in months")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this experience extraction")

class EducationEntry(BaseModel):
    """Schema for a single education entry"""
    institution: str = Field(..., description="Institution name")
    degree: Optional[str] = Field(None, description="Degree obtained")
    start_date: Optional[str] = Field(None, description="Start date in ISO format (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date in ISO format (YYYY-MM-DD)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this education extraction")

class EnhancedResumeData(BaseModel):
    """Enhanced schema for parsed resume data"""
    resume_id: Optional[UUID] = Field(None, description="Resume ID")
    name: str = Field("", description="Candidate name")
    emails: List[str] = Field(default_factory=list, description="Email addresses")
    phones: List[str] = Field(default_factory=list, description="Phone numbers")
    urls: List[str] = Field(default_factory=list, description="URLs (websites, portfolios)")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    summary: str = Field("", description="Professional summary")
    skills: List[SkillEntry] = Field(default_factory=list, description="Extracted skills")
    experiences: List[ExperienceEntry] = Field(default_factory=list, description="Work experiences")
    education: List[EducationEntry] = Field(default_factory=list, description="Education history")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Languages")
    locations: List[str] = Field(default_factory=list, description="Locations")
    raw_text: str = Field("", description="Raw extracted text")
    ocr_used: bool = Field(False, description="Whether OCR was used for text extraction")
    parsing_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall parsing confidence")
    generated_at: str = Field(..., description="Timestamp when parsing was completed")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Source of each extracted field")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "emails": ["john.doe@example.com"],
                "phones": ["+1-555-123-4567"],
                "urls": ["https://johndoe.com"],
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "summary": "Experienced software engineer with 5+ years in web development",
                "skills": [
                    {
                        "skill": "Python",
                        "confidence": 0.95,
                        "source": "exact_match"
                    },
                    {
                        "skill": "React",
                        "confidence": 0.90,
                        "source": "fuzzy_match"
                    }
                ],
                "experiences": [
                    {
                        "company": "Tech Corp",
                        "title": "Senior Software Engineer",
                        "start_date": "2020-01-01",
                        "end_date": "2023-12-31",
                        "bullets": [
                            "Led development of web applications",
                            "Mentored junior developers"
                        ],
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
                "raw_text": "John Doe\nEmail: john.doe@example.com\n...",
                "ocr_used": False,
                "parsing_confidence": 0.88,
                "generated_at": "2023-12-01T10:30:00Z",
                "provenance": {
                    "contact_extraction": "regex",
                    "entity_recognition": "spacy",
                    "skill_extraction": "taxonomy_matching"
                }
            }
        }

class ResumeParseRequest(BaseModel):
    """Schema for resume parse request"""
    background: bool = Field(False, description="Whether to parse in background")
    use_llm: bool = Field(True, description="Whether to use LLM for refinement")
    generate_vectors: bool = Field(False, description="Whether to generate vector embeddings")

class ResumeValidateRequest(BaseModel):
    """Schema for resume validation/correction request"""
    corrections: Dict[str, Any] = Field(..., description="Corrections to apply to parsed data")
    user_id: UUID = Field(..., description="ID of user making the corrections")

class ResumeReviewResponse(BaseModel):
    """Schema for resume review response"""
    resume_id: UUID = Field(..., description="Resume ID")
    parsed_data: EnhancedResumeData = Field(..., description="Parsed resume data")
    raw_text: str = Field(..., description="Raw extracted text")
    highlighted_spans: List[Dict[str, Any]] = Field(default_factory=list, description="Highlighted text spans for review")

# JSON Schema for the enhanced resume data
RESUME_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "resume_id": {
            "type": ["string", "null"],
            "format": "uuid"
        },
        "name": {
            "type": "string"
        },
        "emails": {
            "type": "array",
            "items": {
                "type": "string",
                "format": "email"
            }
        },
        "phones": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "urls": {
            "type": "array",
            "items": {
                "type": "string",
                "format": "uri"
            }
        },
        "linkedin": {
            "type": ["string", "null"],
            "format": "uri"
        },
        "github": {
            "type": ["string", "null"],
            "format": "uri"
        },
        "summary": {
            "type": "string"
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "source": {
                        "type": "string"
                    }
                },
                "required": ["skill", "confidence", "source"]
            }
        },
        "experiences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "start_date": {
                        "type": ["string", "null"],
                        "format": "date"
                    },
                    "end_date": {
                        "type": ["string", "null"],
                        "format": "date"
                    },
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "duration_months": {
                        "type": ["integer", "null"],
                        "minimum": 0
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    }
                },
                "required": ["company", "title", "confidence"]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {
                        "type": "string"
                    },
                    "degree": {
                        "type": ["string", "null"]
                    },
                    "start_date": {
                        "type": ["string", "null"],
                        "format": "date"
                    },
                    "end_date": {
                        "type": ["string", "null"],
                        "format": "date"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    }
                },
                "required": ["institution", "confidence"]
            }
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "locations": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "raw_text": {
            "type": "string"
        },
        "ocr_used": {
            "type": "boolean"
        },
        "parsing_confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "generated_at": {
            "type": "string",
            "format": "date-time"
        },
        "provenance": {
            "type": "object"
        }
    },
    "required": [
        "name",
        "emails",
        "phones",
        "urls",
        "summary",
        "skills",
        "experiences",
        "education",
        "certifications",
        "languages",
        "locations",
        "raw_text",
        "ocr_used",
        "parsing_confidence",
        "generated_at",
        "provenance"
    ]
}
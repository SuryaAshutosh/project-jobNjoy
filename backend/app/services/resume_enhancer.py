"""
Enhanced resume parsing and analysis service
"""
from typing import Dict, Any, List
import re
from datetime import datetime
from app.schemas.resume_schema import EnhancedResumeData

class ResumeEnhancer:
    def __init__(self):
        pass
        
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common tech skills keywords
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express',
            'sql', 'mongodb', 'postgresql', 'mysql', 'docker', 'kubernetes', 'aws', 'azure',
            'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'nlp', 'computer vision',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'less', 'typescript', 'php',
            'ruby', 'rails', 'django', 'flask', 'spring', 'hibernate', 'maven', 'gradle',
            'git', 'jenkins', 'ci/cd', 'agile', 'scrum', 'jira', 'confluence'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
                
        return list(set(found_skills))  # Remove duplicates
        
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        # Simple pattern matching for experience sections
        experience_pattern = r'(?:experience|work history|employment)(?:.*?)(?=(?:education|skills|projects|certifications)|$)'
        experience_match = re.search(experience_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not experience_match:
            return []
            
        experience_text = experience_match.group(0)
        
        # Simple pattern for job entries (very basic)
        job_pattern = r'([A-Za-z\s]+(?:[A-Za-z\s]+)?)\s*\n\s*([A-Za-z\s]+(?:[A-Za-z\s]+)?)\s*\n\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\w\s\d,]*?(?:\n|$)'
        job_matches = re.findall(job_pattern, experience_text, re.IGNORECASE)
        
        experiences = []
        for match in job_matches:
            experiences.append({
                "position": match[0].strip(),
                "company": match[1].strip(),
                "duration": "Unknown",
                "description": "Details extracted from resume"
            })
            
        return experiences
        
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education details from resume text"""
        education_pattern = r'(?:education|academic background)(?:.*?)(?=(?:experience|skills|projects|certifications)|$)'
        education_match = re.search(education_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not education_match:
            return []
            
        education_text = education_match.group(0)
        
        # Simple pattern for education entries
        edu_pattern = r'([A-Za-z\s]+(?:[A-Za-z\s]+)?)\s*\n\s*([A-Za-z\s]+(?:[A-Za-z\s]+)?)\s*\n\s*(?:\d{4})'
        edu_matches = re.findall(edu_pattern, education_text, re.IGNORECASE)
        
        educations = []
        for match in edu_matches:
            educations.append({
                "degree": match[0].strip(),
                "institution": match[1].strip(),
                "year": "Unknown"
            })
            
        return educations
        
    def enhance_parsed_data(self, raw_text: str, parsed_data: Dict[str, Any]) -> EnhancedResumeData:
        """Enhance parsed resume data with additional insights"""
        # Extract additional information
        skills = self.extract_skills(raw_text)
        experiences = self.extract_experience(raw_text)
        education = self.extract_education(raw_text)
        
        # Merge with existing parsed data
        enhanced_data = {
            "personal_info": parsed_data.get("personal_info", {}),
            "summary": parsed_data.get("summary", ""),
            "experience": experiences if experiences else parsed_data.get("experience", []),
            "education": education if education else parsed_data.get("education", []),
            "skills": list(set(skills + parsed_data.get("skills", []))),  # Combine and deduplicate
            "projects": parsed_data.get("projects", []),
            "certifications": parsed_data.get("certifications", []),
            "languages": parsed_data.get("languages", []),
            "extracted_at": datetime.utcnow().isoformat()
        }
        
        return EnhancedResumeData(**enhanced_data)
        
    def analyze_resume_quality(self, parsed_data: EnhancedResumeData) -> Dict[str, Any]:
        """Analyze the quality of a parsed resume"""
        score = 0
        suggestions = []
        
        # Check for essential sections
        if parsed_data.personal_info:
            score += 20
        else:
            suggestions.append("Add personal contact information")
            
        if parsed_data.summary:
            score += 15
        else:
            suggestions.append("Add a professional summary")
            
        if parsed_data.experience:
            score += 25
        else:
            suggestions.append("Add work experience details")
            
        if parsed_data.education:
            score += 15
        else:
            suggestions.append("Add education details")
            
        if parsed_data.skills:
            score += 15
        else:
            suggestions.append("List relevant skills")
            
        if len(parsed_data.skills) >= 5:
            score += 10
        else:
            suggestions.append("Include more specific skills (aim for 5+)")
            
        return {
            "quality_score": min(score, 100),
            "suggestions": suggestions
        }

# Global instance
resume_enhancer = ResumeEnhancer()
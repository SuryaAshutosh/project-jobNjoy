"""
Job data normalization utility
Standardizes job data from different sources
"""

import re
from datetime import datetime
from typing import Dict, Any, List
import json

# Load skills taxonomy
SKILLS_TAXONOMY = [
    "Python", "Java", "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Express",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "CI/CD", "Git", "Linux", "HTML", "CSS", "TypeScript",
    "C++", "C#", "Go", "Rust", "Swift", "Kotlin", "Scala", "Ruby", "PHP",
    "Machine Learning", "Data Science", "AI", "TensorFlow", "PyTorch", "NLP",
    "DevOps", "Terraform", "Jenkins", "Ansible", "Chef", "Puppet",
    "Cybersecurity", "Blockchain", "IoT", "Mobile Development", "iOS", "Android",
    "UI/UX", "Design", "Product Management", "Agile", "Scrum", "Project Management"
]

def normalize_job_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize job data to standard format
    
    Args:
        job_data: Raw job data dictionary
        
    Returns:
        Normalized job data dictionary
    """
    normalized = job_data.copy()
    
    # Normalize company name (remove extra whitespace, standardize case)
    if 'company' in normalized and normalized['company']:
        normalized['company'] = re.sub(r'\s+', ' ', normalized['company'].strip())
        
    # Normalize title
    if 'title' in normalized and normalized['title']:
        normalized['title'] = re.sub(r'\s+', ' ', normalized['title'].strip())
        
    # Normalize location
    if 'location' in normalized and normalized['location']:
        normalized['location'] = re.sub(r'\s+', ' ', normalized['location'].strip())
        
    # Normalize salary values
    if 'salary_min' in normalized:
        normalized['salary_min'] = _normalize_salary_value(normalized['salary_min'])
        
    if 'salary_max' in normalized:
        normalized['salary_max'] = _normalize_salary_value(normalized['salary_max'])
        
    # Normalize posted date to ISO format
    if 'posted_date' in normalized and normalized['posted_date']:
        normalized['posted_date'] = _normalize_date(normalized['posted_date'])
        
    # Normalize description (clean HTML if present)
    if 'description' in normalized and normalized['description']:
        normalized['description'] = _clean_html(normalized['description'])
        
    # Extract skills from description/title if not provided
    if 'skills' not in normalized or not normalized['skills']:
        normalized['skills'] = _extract_skills(normalized)
        
    # Ensure scraped_at is in ISO format
    if 'scraped_at' not in normalized or not normalized['scraped_at']:
        normalized['scraped_at'] = datetime.utcnow().isoformat()
        
    # Ensure confidence score exists
    if 'confidence' not in normalized:
        normalized['confidence'] = _calculate_confidence(normalized)
        
    return normalized

def _normalize_salary_value(salary) -> int:
    """
    Normalize salary value to integer
    
    Args:
        salary: Salary value (int, float, or string)
        
    Returns:
        Normalized salary as integer
    """
    if salary is None:
        return None
        
    if isinstance(salary, (int, float)):
        return int(salary)
        
    if isinstance(salary, str):
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d\-\.]', '', salary)
        try:
            return int(float(cleaned))
        except:
            return None
            
    return None

def _normalize_date(date_str: str) -> str:
    """
    Normalize date string to ISO format
    
    Args:
        date_str: Date string
        
    Returns:
        ISO formatted date string
    """
    if not date_str:
        return None
        
    # Common date formats to try
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%d %b %Y",
        "%d %B %Y",
        "%Y-%m-%dT%H:%M:%SZ"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat() + 'Z'
        except:
            continue
            
    # If we can't parse it, return as is
    return date_str

def _clean_html(text: str) -> str:
    """
    Clean HTML tags from text
    
    Args:
        text: Text with potential HTML tags
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def _extract_skills(job_data: Dict[str, Any]) -> List[str]:
    """
    Extract skills from job title and description
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        List of extracted skills
    """
    skills = []
    
    # Combine title and description for skill extraction
    text_to_search = ""
    if 'title' in job_data:
        text_to_search += f" {job_data['title']}"
    if 'description' in job_data:
        text_to_search += f" {job_data['description']}"
        
    # Convert to lowercase for case-insensitive matching
    text_lower = text_to_search.lower()
    
    # Match against skills taxonomy
    for skill in SKILLS_TAXONOMY:
        if skill.lower() in text_lower:
            # Use original case from taxonomy
            if skill not in skills:
                skills.append(skill)
                
    return skills

def _calculate_confidence(job_data: Dict[str, Any]) -> float:
    """
    Calculate confidence score based on data completeness
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    required_fields = ['title', 'company', 'description']
    optional_fields = ['url', 'location', 'salary_min', 'salary_max', 'posted_date']
    
    required_present = sum(1 for field in required_fields if job_data.get(field))
    optional_present = sum(1 for field in optional_fields if job_data.get(field))
    
    # Weight required fields more heavily
    confidence = (required_present / len(required_fields)) * 0.7 + \
                 (optional_present / len(optional_fields)) * 0.3
                 
    return round(confidence, 2)
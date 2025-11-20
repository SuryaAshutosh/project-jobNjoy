"""
CRUD operations for Resume model
"""

from sqlalchemy.orm import Session
from app.models.db_models import Resume
from app.schemas.schemas import ResumeUpload
from uuid import UUID
from typing import Dict, Any

def get_resume(db: Session, resume_id: UUID):
    """Get a resume by ID"""
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_resumes_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """Get resumes by user ID with pagination"""
    return db.query(Resume).filter(Resume.user_id == user_id).offset(skip).limit(limit).all()

def create_resume(db: Session, resume: ResumeUpload, user_id: UUID):
    """Create a new resume"""
    db_resume = Resume(
        user_id=user_id,
        file_url=resume.file_url,
        raw_text=resume.raw_text,
        parsed_data=resume.parsed_data
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def update_resume_parsed_data(db: Session, resume_id: UUID, parsed_data: dict):
    """Update resume's parsed data"""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if db_resume:
        db_resume.parsed_data = parsed_data
        db.commit()
        db.refresh(db_resume)
    return db_resume

def update_resume_manual_correction(db: Session, resume_id: UUID, corrections: Dict[str, Any], user_id: UUID):
    """Apply manual corrections to resume's parsed data"""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if db_resume:
        # Merge corrections with existing parsed data
        if db_resume.parsed_data:
            updated_data = db_resume.parsed_data.copy()
            updated_data.update(corrections)
        else:
            updated_data = corrections
            
        db_resume.parsed_data = updated_data
        db.commit()
        db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: UUID):
    """Delete a resume"""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume
"""
CRUD operations for Application model
"""

from sqlalchemy.orm import Session
from app.models.db_models import Application
from app.schemas.schemas import ApplicationCreate
from uuid import UUID
from typing import List

def get_applications_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """Get applications by user ID with pagination"""
    return db.query(Application).filter(Application.user_id == user_id).offset(skip).limit(limit).all()

def get_applications_by_user_with_jobs(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """Get applications by user ID with pagination, including job details"""
    return db.query(Application).join(Job).filter(Application.user_id == user_id).offset(skip).limit(limit).all()

def get_application(db: Session, application_id: UUID):
    """Get an application by ID"""
    return db.query(Application).filter(Application.id == application_id).first()

def get_application_with_job(db: Session, application_id: UUID):
    """Get an application by ID with job details"""
    return db.query(Application).join(Job).filter(Application.id == application_id).first()

def get_applications_by_job(db: Session, job_id: UUID, skip: int = 0, limit: int = 100):
    """Get applications by job ID with pagination"""
    return db.query(Application).filter(Application.job_id == job_id).offset(skip).limit(limit).all()

def create_application(db: Session, application: ApplicationCreate, user_id: UUID):
    """Create a new application"""
    db_application = Application(
        user_id=user_id,
        **application.dict()
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application_status(db: Session, application_id: UUID, status: str, notes: str = None):
    """Update application status"""
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if db_application:
        db_application.status = status
        if notes:
            db_application.notes = notes
        db.commit()
        db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: UUID):
    """Delete an application"""
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if db_application:
        db.delete(db_application)
        db.commit()
    return db_application
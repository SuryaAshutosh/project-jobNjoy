"""
CRUD operations for Job and JobSource models
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db_models import Job, JobSource
from app.schemas.schemas import JobCreate, JobSourceCreate
from uuid import UUID
from typing import List, Optional

def get_job(db: Session, job_id: UUID):
    """Get a job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()

def get_job_with_source(db: Session, job_id: UUID):
    """Get a job by ID with source information"""
    return db.query(Job).filter(Job.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100, keyword: str = None, location: str = None, source_id: UUID = None, skill: str = None):
    """Get jobs with filtering and pagination"""
    query = db.query(Job)
    
    if keyword:
        query = query.filter(
            Job.title.ilike(f"%{keyword}%") | 
            Job.description.ilike(f"%{keyword}%") | 
            Job.company.ilike(f"%{keyword}%")
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if source_id:
        query = query.filter(Job.source_id == source_id)
    
    if skill:
        query = query.filter(Job.skills.contains([skill]))
    
    return query.offset(skip).limit(limit).all()

def get_jobs_with_sources(db: Session, skip: int = 0, limit: int = 100, keyword: str = None, location: str = None, source_id: UUID = None, skill: str = None):
    """Get jobs with filtering and pagination, including source information"""
    query = db.query(Job).join(JobSource)
    
    if keyword:
        query = query.filter(
            Job.title.ilike(f"%{keyword}%") | 
            Job.description.ilike(f"%{keyword}%") | 
            Job.company.ilike(f"%{keyword}%")
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if source_id:
        query = query.filter(Job.source_id == source_id)
    
    if skill:
        query = query.filter(Job.skills.contains([skill]))
    
    return query.offset(skip).limit(limit).all()

def get_jobs_count(db: Session, keyword: str = None, location: str = None, source_id: UUID = None, skill: str = None):
    """Get count of jobs with filtering"""
    query = db.query(func.count(Job.id))
    
    if keyword:
        query = query.filter(
            Job.title.ilike(f"%{keyword}%") | 
            Job.description.ilike(f"%{keyword}%") | 
            Job.company.ilike(f"%{keyword}%")
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if source_id:
        query = query.filter(Job.source_id == source_id)
    
    if skill:
        query = query.filter(Job.skills.contains([skill]))
    
    return query.scalar()

def create_job(db: Session, job: JobCreate):
    """Create a new job"""
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job_source(db: Session, source_id: UUID):
    """Get a job source by ID"""
    return db.query(JobSource).filter(JobSource.id == source_id).first()

def get_job_sources(db: Session, skip: int = 0, limit: int = 100):
    """Get job sources with pagination"""
    return db.query(JobSource).offset(skip).limit(limit).all()

def create_job_source(db: Session, job_source: JobSourceCreate):
    """Create a new job source"""
    db_job_source = JobSource(**job_source.dict())
    db.add(db_job_source)
    db.commit()
    db.refresh(db_job_source)
    return db_job_source

def get_or_create_job_source(db: Session, name: str, base_url: str):
    """Get or create a job source by name"""
    job_source = db.query(JobSource).filter(JobSource.name == name).first()
    if not job_source:
        job_source = JobSource(name=name, base_url=base_url)
        db.add(job_source)
        db.commit()
        db.refresh(job_source)
    return job_source
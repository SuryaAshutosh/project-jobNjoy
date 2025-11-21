"""
Jobs router for JobBuddy
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.schemas import JobCreate, JobResponse, JobSourceCreate, JobSourceResponse
from app.crud.crud_job import create_job, get_job, get_jobs, get_jobs_count, get_job_source, get_job_sources, create_job_source, get_or_create_job_source
from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.tasks import background_task_manager
from app.models.db_models import User
from app.services.job_service import job_service
import json

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    keyword: str = None,
    location: str = None,
    source_id: str = None,
    skill: str = None,
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of jobs with optional filtering
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        keyword: Search keyword (title, company, description)
        location: Location filter
        source_id: Job source ID filter
        skill: Skill filter
        db: Database session
        
    Returns:
        List[JobResponse]: List of jobs
    """
    jobs = get_jobs_with_sources(db, skip, limit, keyword, location, source_id, skill)
    return jobs

@router.get("/count")
async def get_jobs_count_endpoint(
    keyword: str = None,
    location: str = None,
    source_id: str = None,
    skill: str = None,
    db: Session = Depends(get_db)
):
    """
    Get the count of jobs with optional filtering
    
    Args:
        keyword: Search keyword (title, company, description)
        location: Location filter
        source_id: Job source ID filter
        skill: Skill filter
        db: Database session
        
    Returns:
        dict: Count of jobs
    """
    count = get_jobs_count(db, keyword, location, source_id, skill)
    return {"count": count}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a job by ID
    
    Args:
        job_id: The ID of the job to retrieve
        db: Database session
        
    Returns:
        JobResponse: The requested job
    """
    db_job = get_job_with_source(db, job_id)
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return db_job

@router.post("/scrape")
async def trigger_job_scraping(
    source_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Trigger job scraping for a specific source (admin only)
    
    Args:
        source_id: The ID of the job source to scrape
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        dict: Scraping status
    """
    # Verify job source exists
    job_source = get_job_source(db, source_id)
    if not job_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    
    # Trigger scraping in background
    background_task_manager.add_task(scrape_jobs_task, source_id)
    
    return {"status": "scraping_started", "source_id": source_id}

@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_jobs(
    jobs_data: List[JobCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Import jobs from agent (admin/system token only)
    
    Args:
        jobs_data: List of jobs to import
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        dict: Import status
    """
    created_jobs = []
    
    for job_data in jobs_data:
        # Create job source if it doesn't exist
        job_source = get_or_create_job_source(db, "Agent Import", "https://agent-import")
        
        # Update job data with source ID if not provided
        if not job_data.source_id:
            job_data.source_id = job_source.id
        
        # Create job
        db_job = create_job(db, job_data)
        created_jobs.append(db_job)
    
    # Notify subscribers about new jobs
    await job_service.process_new_jobs(created_jobs)
    
    return {
        "status": "imported",
        "count": len(created_jobs),
        "jobs": [job.id for job in created_jobs]
    }

@router.get("/sources/", response_model=List[JobSourceResponse])
async def list_job_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of job sources
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[JobSourceResponse]: List of job sources
    """
    sources = get_job_sources(db, skip, limit)
    return sources

@router.post("/sources/", response_model=JobSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_job_source_endpoint(
    job_source: JobSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new job source (admin only)
    
    Args:
        job_source: Job source data
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        JobSourceResponse: The created job source
    """
    db_job_source = create_job_source(db, job_source)
    return db_job_source

# Background task function
def scrape_jobs_task(source_id: str):
    """
    Background task to scrape jobs from a source
    
    Args:
        source_id: The ID of the job source to scrape
    """
    from app.db import SessionLocal
    
    db = SessionLocal()
    try:
        # In a real implementation, this would:
        # 1. Connect to the job source
        # 2. Scrape job listings
        # 3. Parse job data
        # 4. Save jobs to the database
        
        print(f"Scraping jobs from source {source_id}")
        return {"status": "completed", "source_id": source_id}
    except Exception as e:
        print(f"Error scraping jobs from source {source_id}: {str(e)}")
        return {"status": "error", "source_id": source_id, "error": str(e)}
    finally:
        db.close()
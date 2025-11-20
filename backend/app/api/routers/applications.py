"""
Applications router for JobBuddy
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.schemas import ApplicationCreate, ApplicationResponse
from app.crud.crud_application import create_application, get_application, get_applications_by_user, update_application_status
from app.crud.crud_job import get_job
from app.core.auth import get_current_active_user
from app.core.tasks import background_task_manager
from app.services.agent_client import agent_client
from app.models.db_models import User
import json

router = APIRouter()

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application_endpoint(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new job application
    
    Args:
        application: Application data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ApplicationResponse: The created application
    """
    # Verify job exists
    job = get_job(db, application.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Create application
    db_application = create_application(db, application, current_user.id)
    return db_application

@router.post("/{application_id}/auto-apply")
async def start_auto_apply(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start auto-apply background workflow for an application
    
    Args:
        application_id: The ID of the application to auto-apply
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Auto-apply status
    """
    # Get application
    db_application = get_application(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user owns this application
    if str(db_application.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to auto-apply for this application"
        )
    
    # Trigger auto-apply in background
    background_task_manager.add_task(auto_apply_task, application_id)
    
    return {"status": "auto_apply_started", "application_id": application_id}

@router.post("/agent-result")
async def submit_application_result(
    application_id: str,
    status: str,
    notes: str = None,
    x_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Receive application result from Qoder Auto-Apply agent
    
    Args:
        application_id: The ID of the application
        status: The new status
        notes: Additional notes
        x_signature: Agent signature for authentication
        db: Database session
        
    Returns:
        dict: Update status
    """
    # Verify agent signature (simplified for this example)
    # In a real implementation, you would verify the signature properly
    # agent_client.authenticate_agent_request(json.dumps(await request.json()), x_signature)
    
    # Update application status
    updated_application = update_application_status(db, application_id, status, notes)
    
    if not updated_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return {"status": "updated", "application_id": application_id}

@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of applications for the current user
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ApplicationResponse]: List of applications
    """
    applications = get_applications_by_user(db, current_user.id, skip, limit)
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application_by_id(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get an application by ID
    
    Args:
        application_id: The ID of the application to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ApplicationResponse: The requested application
    """
    db_application = get_application(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user owns this application
    if str(db_application.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this application"
        )
    
    return db_application

# Background task function
def auto_apply_task(application_id: str):
    """
    Background task to auto-apply for a job
    
    Args:
        application_id: The ID of the application to process
    """
    from app.db import SessionLocal
    
    db = SessionLocal()
    try:
        # In a real implementation, this would:
        # 1. Retrieve application details
        # 2. Connect to the job portal
        # 3. Fill out application forms
        # 4. Submit the application
        # 5. Update application status
        
        print(f"Auto-applying for application {application_id}")
        return {"status": "completed", "application_id": application_id}
    except Exception as e:
        print(f"Error auto-applying for application {application_id}: {str(e)}")
        
        # Update application status to failed
        update_application_status(db, application_id, "failed", str(e))
        
        return {"status": "error", "application_id": application_id, "error": str(e)}
    finally:
        db.close()
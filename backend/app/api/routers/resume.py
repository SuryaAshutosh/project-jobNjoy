"""
Enhanced Resume router for JobBuddy with NLP and LLM capabilities
"""

import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db import get_db
from app.schemas.schemas import ResumeUpload, ResumeResponse
from app.schemas.resume_schema import (
    ResumeParseRequest, 
    ResumeValidateRequest, 
    ResumeReviewResponse,
    EnhancedResumeData
)
from app.crud.crud_resume import (
    create_resume, 
    get_resume, 
    get_resumes_by_user, 
    update_resume_parsed_data, 
    delete_resume,
    update_resume_manual_correction
)
from app.core.auth import get_current_active_user
from app.core.storage import storage_client, generate_file_key, sanitize_filename
from app.core.tasks import background_task_manager
from app.services.resume_parser import resume_parser_service
from app.services.llm_adapter import llm_adapter
from app.services.vector_service import vector_service
from app.services.resume_enhancer import resume_enhancer
from app.models.db_models import User, Resume, AILog
from app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a resume file (PDF/DOCX/TXT)
    
    Args:
        file: The resume file to upload
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ResumeResponse: The created resume record
    """
    # Validate file type
    allowed_types = [
        "application/pdf", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed."
        )
    
    # Validate file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes."
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Generate file key
    file_key = generate_file_key(str(current_user.id), safe_filename)
    
    # Upload file to storage
    file_url = storage_client.upload_file(file, file_key)
    
    # Create resume record in database
    resume_data = ResumeUpload(
        file_url=file_url,
        raw_text="",  # Will be populated during parsing
        parsed_data=None  # Will be populated during parsing
    )
    
    db_resume = create_resume(db, resume_data, current_user.id)
    
    # Trigger resume parsing in background
    # Note: FastAPI's BackgroundTasks doesn't support passing database sessions directly
    # We need to use a different approach for background parsing
    background_tasks.add_task(trigger_resume_parsing, str(db_resume.id))
    
    return db_resume

def trigger_resume_parsing(resume_id: str):
    """
    Trigger resume parsing in a separate process
    
    Args:
        resume_id: The ID of the resume to parse
    """
    # Create a new database session for the background task
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        # Use the existing background task manager
        background_task_manager.add_task(parse_resume_background_task, resume_id, db)
    except Exception as e:
        print(f"Error triggering resume parsing for {resume_id}: {str(e)}")
    finally:
        db.close()

@router.post("/{resume_id}/parse")
async def parse_resume(
    resume_id: UUID,
    parse_request: ResumeParseRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger parsing of a resume
    
    Args:
        resume_id: The ID of the resume to parse
        parse_request: Parsing options
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Parsing status
    """
    # Get resume
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user owns this resume
    if str(db_resume.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to parse this resume"
        )
    
    # Use default parse request if not provided
    if parse_request is None:
        parse_request = ResumeParseRequest()
    
    # Trigger resume parsing
    if parse_request.background:
        # Background parsing
        background_task_manager.add_task(
            parse_resume_background_task, 
            str(resume_id), 
            db,
            parse_request.use_llm,
            parse_request.generate_vectors
        )
        return {"status": "parsing_started", "resume_id": str(resume_id), "mode": "background"}
    else:
        # Synchronous parsing
        try:
            result = parse_resume_sync(
                str(resume_id), 
                db, 
                parse_request.use_llm, 
                parse_request.generate_vectors
            )
            return {"status": "completed", "resume_id": str(resume_id), "result": result}
        except Exception as e:
            return {"status": "error", "resume_id": str(resume_id), "error": str(e)}

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume_by_id(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a resume by ID
    
    Args:
        resume_id: The ID of the resume to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ResumeResponse: The requested resume
    """
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user owns this resume
    if str(db_resume.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )
    
    return db_resume

@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List resumes for the current user
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[ResumeResponse]: List of resumes
    """
    resumes = get_resumes_by_user(db, current_user.id, skip, limit)
    return resumes

@router.delete("/{resume_id}")
async def delete_resume_by_id(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a resume by ID
    
    Args:
        resume_id: The ID of the resume to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Deletion status
    """
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user owns this resume
    if str(db_resume.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this resume"
        )
    
    # Delete file from storage
    # Extract file key from URL (simplified)
    if db_resume.file_url.startswith("http://localhost:8000/uploads/"):
        file_key = db_resume.file_url.replace("http://localhost:8000/uploads/", "")
        storage_client.delete_file(file_key)
    
    # Delete resume record from database
    delete_resume(db, resume_id)
    
    return {"status": "deleted", "resume_id": str(resume_id)}

@router.post("/validate/{resume_id}")
async def validate_resume(
    resume_id: UUID,
    validate_request: ResumeValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Apply manual corrections to a parsed resume
    
    Args:
        resume_id: The ID of the resume to validate
        validate_request: Validation/correction data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Validation status
    """
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user owns this resume
    if str(db_resume.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to validate this resume"
        )
    
    try:
        # Store audit log for the edit
        ai_log = AILog(
            user_id=current_user.id,
            action="manual_edit",
            input_data=db_resume.parsed_data,  # Before
            output_data=validate_request.corrections  # After
        )
        db.add(ai_log)
        db.commit()
        
        # Apply corrections
        update_resume_manual_correction(
            db, 
            resume_id, 
            validate_request.corrections, 
            validate_request.user_id
        )
        
        return {
            "status": "validated", 
            "resume_id": str(resume_id),
            "applied_corrections": validate_request.corrections
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate resume: {str(e)}"
        )

@router.get("/review/{resume_id}", response_model=ResumeReviewResponse)
async def review_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get resume data for manual review
    
    Args:
        resume_id: The ID of the resume to review
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ResumeReviewResponse: Resume data for review
    """
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user owns this resume
    if str(db_resume.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to review this resume"
        )
    
    # Parse the raw text to identify key sections for highlighting
    highlighted_spans = []
    if db_resume.raw_text:
        # Simple highlighting of key sections (would be enhanced in production)
        sections = ["experience", "education", "skills", "summary"]
        for section in sections:
            if section in db_resume.raw_text.lower():
                highlighted_spans.append({
                    "section": section,
                    "text": section.title()
                })
    
    # Convert parsed_data to EnhancedResumeData if it exists
    parsed_data = {}
    if db_resume.parsed_data:
        try:
            parsed_data = EnhancedResumeData(**db_resume.parsed_data)
        except Exception:
            # If conversion fails, use raw data
            parsed_data = db_resume.parsed_data
    
    return ResumeReviewResponse(
        resume_id=resume_id,
        parsed_data=parsed_data,
        raw_text=db_resume.raw_text or "",
        highlighted_spans=highlighted_spans
    )

# Background task functions
def parse_resume_background_task(
    resume_id: str, 
    db: Session, 
    use_llm: bool = True, 
    generate_vectors: bool = False
):
    """
    Background task to parse a resume
    
    Args:
        resume_id: The ID of the resume to parse
        db: Database session
        use_llm: Whether to use LLM for refinement
        generate_vectors: Whether to generate vector embeddings
    """
    try:
        result = parse_resume_sync(resume_id, db, use_llm, generate_vectors)
        return {"status": "completed", "resume_id": resume_id, "result": result}
    except Exception as e:
        print(f"Error parsing resume {resume_id}: {str(e)}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        return {"status": "error", "resume_id": resume_id, "error": str(e)}

def parse_resume_sync(
    resume_id: str, 
    db: Session, 
    use_llm: bool = True, 
    generate_vectors: bool = False
):
    """
    Synchronously parse a resume
    
    Args:
        resume_id: The ID of the resume to parse
        db: Database session
        use_llm: Whether to use LLM for refinement
        generate_vectors: Whether to generate vector embeddings
        
    Returns:
        dict: Parsing result
    """
    # Get resume
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        raise Exception("Resume not found")
    
    # Process resume file
    print(f"Processing resume file: {db_resume.file_url}")
    result = resume_parser_service.process_resume_file(db_resume.file_url)
    
    # Apply LLM refinement if requested
    if use_llm:
        try:
            result["parsed_data"] = llm_adapter.normalize_parsed_data(result["parsed_data"])
        except Exception as e:
            print(f"LLM refinement failed for resume {resume_id}: {str(e)}")
            # Continue without LLM refinement
    
    # Enhance parsed data with additional insights
    try:
        enhanced_data = resume_enhancer.enhance_parsed_data(db_resume.raw_text, result["parsed_data"])
        result["parsed_data"] = enhanced_data.dict()
        
        # Analyze resume quality
        quality_analysis = resume_enhancer.analyze_resume_quality(enhanced_data)
        result["parsed_data"]["quality_analysis"] = quality_analysis
    except Exception as e:
        print(f"Resume enhancement failed for resume {resume_id}: {str(e)}")
        # Continue without enhancement
    
    # Generate vectors if requested
    if generate_vectors:
        try:
            vectors = vector_service.create_resume_vectors(result["parsed_data"])
            result["parsed_data"]["vectors"] = vectors
        except Exception as e:
            print(f"Vector generation failed for resume {resume_id}: {str(e)}")
            # Continue without vectors
    
    # Update resume with parsed data
    update_resume_parsed_data(db, resume_id, result["parsed_data"])
    
    return result

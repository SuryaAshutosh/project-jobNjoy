"""
Dashboard router for JobBuddy - statistics and metrics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.core.auth import get_current_active_user
from app.models.db_models import User, Job, Application
from app.crud.crud_application import get_applications_by_user
from typing import Dict, Any

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard statistics for the current user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Dashboard statistics
    """
    # Get total jobs scraped
    total_jobs = db.query(func.count(Job.id)).scalar()
    
    # Get user's applications
    user_applications = get_applications_by_user(db, current_user.id)
    
    # Count application statuses
    applied_count = sum(1 for app in user_applications if app.status == "applied")
    pending_count = sum(1 for app in user_applications if app.status == "pending")
    failed_count = sum(1 for app in user_applications if app.status == "failed")
    
    # Get user subscription status
    subscription_status = current_user.subscription_status
    
    stats = {
        "jobs_scraped": total_jobs,
        "applications_submitted": len(user_applications),
        "applied_success": applied_count,
        "pending_applications": pending_count,
        "failed_applications": failed_count,
        "user_subscription_status": subscription_status
    }
    
    return stats

@router.get("/applications/chart")
async def get_applications_chart_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get application data for chart visualization
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Chart data
    """
    # This would typically return data for a chart showing applications over time
    # For now, we'll return a simple structure
    
    user_applications = get_applications_by_user(db, current_user.id)
    
    # Group by status
    status_counts = {}
    for app in user_applications:
        status = app.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    chart_data = {
        "labels": list(status_counts.keys()),
        "data": list(status_counts.values())
    }
    
    return chart_data

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent user activity
    
    Args:
        limit: Number of recent activities to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Recent activity data
    """
    # Get recent applications
    recent_applications = db.query(Application)\
        .filter(Application.user_id == current_user.id)\
        .order_by(Application.created_at.desc())\
        .limit(limit)\
        .all()
    
    activity = []
    for app in recent_applications:
        # Get job details
        job = db.query(Job).filter(Job.id == app.job_id).first()
        
        activity.append({
            "type": "application",
            "status": app.status,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "timestamp": app.created_at.isoformat()
        })
    
    return {"activity": activity}
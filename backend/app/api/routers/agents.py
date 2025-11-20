"""
Agents router for JobBuddy - endpoints for Qoder agents to call
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db import get_db
from app.core.auth import get_current_admin_user
from app.services.agent_client import agent_client
from app.models.db_models import User
import json

router = APIRouter()

@router.post("/register-run")
async def register_agent_run(
    agent_id: str,
    run_data: Dict[str, Any],
    x_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Register an agent run
    
    Args:
        agent_id: The ID of the agent
        run_data: Data about the agent run
        x_signature: Agent signature for authentication
        db: Database session
        
    Returns:
        dict: Registration response
    """
    # In a real implementation, you would verify the agent signature
    # For now, we'll just log the registration
    
    result = agent_client.register_agent_run(agent_id, run_data)
    return result

@router.post("/update-run-status")
async def update_agent_run_status(
    run_id: str,
    status: str,
    details: Dict[str, Any] = None,
    x_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Update the status of an agent run
    
    Args:
        run_id: The ID of the agent run
        status: The new status
        details: Additional details about the status update
        x_signature: Agent signature for authentication
        db: Database session
        
    Returns:
        dict: Status update response
    """
    # In a real implementation, you would verify the agent signature
    # For now, we'll just log the status update
    
    result = agent_client.update_agent_run_status(run_id, status, details)
    return result

@router.post("/trigger-workflow")
async def trigger_agent_workflow(
    agent_type: str,
    workflow_data: Dict[str, Any],
    x_signature: str = Header(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Trigger an agent workflow (admin only)
    
    Args:
        agent_type: The type of agent (e.g., 'scraper', 'auto-apply')
        workflow_data: Data needed for the workflow
        x_signature: Agent signature for authentication
        current_user: Current authenticated user (must be admin)
        db: Database session
        
    Returns:
        dict: Workflow trigger response
    """
    # In a real implementation, you would verify the agent signature
    # For now, we'll just trigger the workflow
    
    result = agent_client.trigger_agent_workflow(agent_type, workflow_data)
    return result

@router.post("/webhook")
async def agent_webhook(
    request: Request,
    x_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for agents to send notifications
    
    Args:
        request: The incoming request
        x_signature: Agent signature for authentication
        db: Database session
        
    Returns:
        dict: Webhook response
    """
    # Get request body
    body = await request.body()
    
    # In a real implementation, you would verify the signature
    # For now, we'll just log the webhook
    
    try:
        payload = json.loads(body.decode())
        print(f"Received agent webhook: {payload}")
        return {"status": "received"}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

# Example endpoint showing how agents should authenticate
@router.get("/auth-example")
async def agent_auth_example():
    """
    Example of how agents should authenticate when calling agent endpoints
    
    Returns:
        dict: Authentication example
    """
    return agent_client.example_agent_authentication()
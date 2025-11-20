"""
Agent client service for JobBuddy - hooks & APIs for Qoder agents to call
"""

import hashlib
import hmac
import os
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Header
from app.core.config import settings

class AgentClient:
    """Service for handling agent communications"""
    
    def __init__(self):
        """Initialize the agent client"""
        self.agent_secret = os.getenv("AGENT_SECRET_KEY", "default-agent-secret")
    
    def verify_agent_signature(self, payload: str, signature: str) -> bool:
        """
        Verify the signature of an agent request
        
        Args:
            payload: The request payload
            signature: The signature from the X-Signature header
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Create HMAC signature
        expected_signature = hmac.new(
            self.agent_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (using hmac.compare_digest for security)
        return hmac.compare_digest(signature, expected_signature)
    
    def authenticate_agent_request(self, payload: str, x_signature: str = Header(...)) -> bool:
        """
        Authenticate an agent request using signature verification
        
        Args:
            payload: The request payload
            x_signature: The X-Signature header
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            HTTPException: If authentication fails
        """
        if not self.verify_agent_signature(payload, x_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid agent signature"
            )
        return True
    
    def register_agent_run(self, agent_id: str, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent run
        
        Args:
            agent_id: The ID of the agent
            run_data: Data about the agent run
            
        Returns:
            Dict: Registration response
        """
        # In a real implementation, this would:
        # 1. Save the agent run to the database
        # 2. Track the agent's progress
        # 3. Log relevant metrics
        # 4. Return a run ID for tracking
        
        print(f"Registering agent run for agent {agent_id}")
        return {
            "status": "registered",
            "agent_id": agent_id,
            "run_data": run_data
        }
    
    def update_agent_run_status(self, run_id: str, status: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update the status of an agent run
        
        Args:
            run_id: The ID of the agent run
            status: The new status
            details: Additional details about the status update
            
        Returns:
            Dict: Status update response
        """
        # In a real implementation, this would:
        # 1. Update the agent run status in the database
        # 2. Log the status change
        # 3. Notify relevant systems if needed
        
        print(f"Updating agent run {run_id} status to {status}")
        return {
            "status": "updated",
            "run_id": run_id,
            "new_status": status,
            "details": details or {}
        }
    
    def trigger_agent_workflow(self, agent_type: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger an agent workflow
        
        Args:
            agent_type: The type of agent (e.g., 'scraper', 'auto-apply')
            workflow_data: Data needed for the workflow
            
        Returns:
            Dict: Workflow trigger response
        """
        # In a real implementation, this would:
        # 1. Queue the workflow for execution
        # 2. Return a workflow ID for tracking
        # 3. Possibly trigger immediate execution
        
        print(f"Triggering {agent_type} workflow")
        return {
            "status": "triggered",
            "agent_type": agent_type,
            "workflow_data": workflow_data
        }

# Global agent client instance
agent_client = AgentClient()

# Utility functions for agent authentication
def generate_agent_signature(payload: str) -> str:
    """
    Generate a signature for agent requests
    
    Args:
        payload: The request payload
        
    Returns:
        str: Generated signature
    """
    agent_secret = os.getenv("AGENT_SECRET_KEY", "default-agent-secret")
    return hmac.new(
        agent_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_agent_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify a webhook signature from an agent
    
    Args:
        payload: The webhook payload
        signature: The signature from the header
        secret: The secret key
        
    Returns:
        bool: True if signature is valid
    """
    expected_signature = "sha256=" + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# Example usage for agents to authenticate when calling endpoints
def example_agent_authentication():
    """
    Example of how agents should authenticate when calling agent endpoints
    
    Agents should:
    1. Create a payload (JSON string of the request body)
    2. Generate a signature using the shared secret
    3. Include the signature in the X-Signature header
    """
    # Example payload
    payload = '{"job_id": "123", "application_id": "456"}'
    
    # Generate signature (this would be done by the agent)
    signature = generate_agent_signature(payload)
    
    # Include in request headers:
    # X-Signature: <signature>
    
    return {
        "payload": payload,
        "signature": signature,
        "headers": {
            "X-Signature": signature
        }
    }
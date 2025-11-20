"""
Backend client for Auto-Apply Agent
Handles communication with the JobBuddy backend API
"""

import asyncio
import aiohttp
import json
import hmac
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .utils.settings import settings

logger = logging.getLogger(__name__)

class BackendClient:
    """Handles communication with the JobBuddy backend API"""
    
    def __init__(self):
        """Initialize backend client"""
        self.backend_url = settings.get("backend.url", "http://localhost:8000").rstrip('/')
        self.agent_secret_key = settings.get("backend.agent_secret_key", "default-agent-secret")
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def _generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for agent requests
        
        Args:
            payload: JSON payload string
            
        Returns:
            HMAC signature
        """
        return hmac.new(
            self.agent_secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
    async def get_pending_applications(self) -> List[Dict[str, Any]]:
        """
        Fetch pending applications that need auto-apply processing
        
        Returns:
            List of pending applications
        """
        try:
            # Prepare request
            url = f"{self.backend_url}/api/applications"
            params = {"status": "pending_auto_apply"}
            
            # Generate signature
            payload = json.dumps(params, sort_keys=True)
            signature = self._generate_signature(payload)
            
            # Make request
            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    applications = await response.json()
                    logger.info(f"Fetched {len(applications)} pending applications")
                    return applications
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to fetch pending applications: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching pending applications: {e}")
            return []
            
    async def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch job details by ID
        
        Args:
            job_id: Job ID
            
        Returns:
            Job details or None if failed
        """
        try:
            # Prepare request
            url = f"{self.backend_url}/api/jobs/{job_id}"
            
            # Generate signature
            payload = json.dumps({}, sort_keys=True)
            signature = self._generate_signature(payload)
            
            # Make request
            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    job_data = await response.json()
                    logger.info(f"Fetched job details for job {job_id}")
                    return job_data
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to fetch job details: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None
            
    async def get_resume_data(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch resume data by ID
        
        Args:
            resume_id: Resume ID
            
        Returns:
            Resume data or None if failed
        """
        try:
            # Prepare request
            url = f"{self.backend_url}/api/resume/{resume_id}"
            
            # Generate signature
            payload = json.dumps({}, sort_keys=True)
            signature = self._generate_signature(payload)
            
            # Make request
            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    resume_data = await response.json()
                    logger.info(f"Fetched resume data for resume {resume_id}")
                    return resume_data
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to fetch resume data: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching resume data: {e}")
            return None
            
    async def submit_application_result(self, application_id: str, status: str, 
                                      notes: str = "", logs: List[str] = None) -> bool:
        """
        Submit application result to backend
        
        Args:
            application_id: Application ID
            status: Application status (applied, failed, manual_needed)
            notes: Additional notes
            logs: Application logs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare request data
            data = {
                "application_id": application_id,
                "status": status,
                "notes": notes,
                "logs": logs or [],
                "applied_at": datetime.utcnow().isoformat() + "Z"
            }
            
            # Prepare request
            url = f"{self.backend_url}/api/agents/submit-application-result"
            payload = json.dumps(data, sort_keys=True)
            signature = self._generate_signature(payload)
            
            # Make request
            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, data=payload, headers=headers) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"Successfully submitted application result for {application_id}: {status}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to submit application result: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error submitting application result: {e}")
            return False
            
    async def update_application_status(self, application_id: str, status: str, 
                                      notes: str = "") -> bool:
        """
        Update application status (simplified version for compatibility)
        
        Args:
            application_id: Application ID
            status: New status
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare request data
            data = {
                "status": status,
                "notes": notes
            }
            
            # Prepare request
            url = f"{self.backend_url}/api/applications/{application_id}/agent-result"
            payload = json.dumps(data, sort_keys=True)
            signature = self._generate_signature(payload)
            
            # Make request
            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, data=payload, headers=headers) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"Successfully updated application status for {application_id}: {status}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update application status: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
            return False

# Global backend client instance
backend_client = None

async def get_backend_client() -> BackendClient:
    """
    Get the global backend client instance
    
    Returns:
        BackendClient instance
    """
    global backend_client
    if backend_client is None:
        backend_client = BackendClient()
    return backend_client
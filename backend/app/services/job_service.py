"""
Job service for real-time job updates and notifications
"""
from typing import List, Dict, Any
from app.models.db_models import Job
from app.schemas.schemas import JobResponse
import asyncio
import json
from datetime import datetime

class JobService:
    def __init__(self):
        self.subscribers = []
        
    async def subscribe_to_job_updates(self, websocket):
        """Subscribe a websocket to job updates"""
        self.subscribers.append(websocket)
        
    async def unsubscribe_from_job_updates(self, websocket):
        """Unsubscribe a websocket from job updates"""
        if websocket in self.subscribers:
            self.subscribers.remove(websocket)
            
    async def notify_job_updates(self, job_data: Dict[str, Any]):
        """Notify all subscribers about job updates"""
        if not self.subscribers:
            return
            
        message = {
            "type": "job_update",
            "data": job_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create a copy of subscribers to avoid modification during iteration
        subscribers_copy = self.subscribers.copy()
        
        for websocket in subscribers_copy:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                # Remove dead connections
                await self.unsubscribe_from_job_updates(websocket)
                
    async def process_new_jobs(self, jobs: List[Job]):
        """Process newly added jobs and notify subscribers"""
        for job in jobs:
            job_data = {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_range": job.salary_range,
                "skills": job.skills,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }
            await self.notify_job_updates(job_data)
            
    async def get_real_time_job_stats(self):
        """Get real-time statistics about job listings"""
        # In a real implementation, this would query the database
        # for current job statistics
        return {
            "total_jobs": 0,
            "new_jobs_last_hour": 0,
            "active_sources": 0
        }

# Global instance
job_service = JobService()
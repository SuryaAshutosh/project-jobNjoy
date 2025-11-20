"""
Job scraping scheduler
Handles periodic execution of scraping tasks
"""

import asyncio
import logging
from typing import Callable, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class JobScheduler:
    """Schedules and manages periodic job scraping tasks"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        
    def add_task(self, name: str, func: Callable, interval: int, 
                 params: Dict[str, Any] = None, immediate: bool = False):
        """
        Add a scheduled task
        
        Args:
            name: Task name
            func: Async function to execute
            interval: Interval in seconds
            params: Parameters to pass to the function
            immediate: Whether to run immediately on start
        """
        self.tasks[name] = {
            'func': func,
            'interval': interval,
            'params': params or {},
            'immediate': immediate,
            'last_run': None,
            'next_run': datetime.now() if immediate else datetime.now() + timedelta(seconds=interval)
        }
        
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
            
    async def start(self):
        """Start the scheduler"""
        self.running = True
        logger.info("Job scheduler started")
        
        # Run immediate tasks first
        immediate_tasks = [
            name for name, task in self.tasks.items() if task['immediate']
        ]
        
        for task_name in immediate_tasks:
            await self._run_task(task_name)
            
        # Main scheduling loop
        while self.running:
            now = datetime.now()
            
            # Check which tasks need to run
            for task_name, task in self.tasks.items():
                if now >= task['next_run']:
                    await self._run_task(task_name)
                    task['next_run'] = now + timedelta(seconds=task['interval'])
                    
            # Sleep briefly to avoid busy waiting
            await asyncio.sleep(1)
            
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Job scheduler stopped")
        
    async def _run_task(self, task_name: str):
        """Run a scheduled task"""
        try:
            task = self.tasks[task_name]
            logger.info(f"Running scheduled task: {task_name}")
            
            # Execute the task function
            if asyncio.iscoroutinefunction(task['func']):
                await task['func'](**task['params'])
            else:
                task['func'](**task['params'])
                
            task['last_run'] = datetime.now()
            logger.info(f"Completed scheduled task: {task_name}")
            
        except Exception as e:
            logger.error(f"Error running scheduled task {task_name}: {e}")
            
    def get_task_status(self) -> List[Dict[str, Any]]:
        """Get status of all scheduled tasks"""
        status = []
        now = datetime.now()
        
        for name, task in self.tasks.items():
            status.append({
                'name': name,
                'interval': task['interval'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat(),
                'due': now >= task['next_run']
            })
            
        return status
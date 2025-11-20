"""
Job deduplication utility
Removes duplicate job listings using multiple strategies
"""

import hashlib
from typing import Dict, Any, List
from rapidfuzz import fuzz

class Deduplicator:
    """Handles job deduplication using multiple strategies"""
    
    def __init__(self, similarity_threshold: float = 92.0):
        """
        Initialize deduplicator
        
        Args:
            similarity_threshold: Threshold for fuzzy matching (0-100)
        """
        self.similarity_threshold = similarity_threshold
        self.seen_jobs = set()  # For exact duplicate detection
        self.job_signatures = {}  # For fuzzy duplicate detection
        
    def is_duplicate(self, job_data: Dict[str, Any]) -> bool:
        """
        Check if a job is a duplicate using multiple strategies
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            True if job is a duplicate
        """
        # Strategy 1: Exact duplicate based on source_name + source_id
        if self._is_exact_duplicate(job_data):
            return True
            
        # Strategy 2: Fuzzy duplicate based on title + company + location
        if self._is_fuzzy_duplicate(job_data):
            return True
            
        return False
        
    def _is_exact_duplicate(self, job_data: Dict[str, Any]) -> bool:
        """
        Check for exact duplicates using source_name + source_id
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            True if exact duplicate
        """
        source_name = job_data.get('source_name', '')
        source_id = job_data.get('source_id', '')
        
        if source_name and source_id:
            key = f"{source_name}:{source_id}"
            if key in self.seen_jobs:
                return True
            return False
            
        return False
        
    def _is_fuzzy_duplicate(self, job_data: Dict[str, Any]) -> bool:
        """
        Check for fuzzy duplicates using title + company + location
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            True if fuzzy duplicate
        """
        title = job_data.get('title', '').lower().strip()
        company = job_data.get('company', '').lower().strip()
        location = job_data.get('location', '').lower().strip()
        
        if not title or not company:
            return False
            
        # Create signature for fuzzy matching
        signature = f"{title}|{company}|{location}"
        
        # Compare against existing signatures
        for existing_signature, existing_job in self.job_signatures.items():
            similarity = fuzz.ratio(signature, existing_signature)
            if similarity >= self.similarity_threshold:
                return True
                
        return False
        
    def add_job(self, job_data: Dict[str, Any]):
        """
        Add job to tracking sets
        
        Args:
            job_data: Job data dictionary
        """
        # Add to exact duplicate tracking
        source_name = job_data.get('source_name', '')
        source_id = job_data.get('source_id', '')
        
        if source_name and source_id:
            key = f"{source_name}:{source_id}"
            self.seen_jobs.add(key)
            
        # Add to fuzzy duplicate tracking
        title = job_data.get('title', '').lower().strip()
        company = job_data.get('company', '').lower().strip()
        location = job_data.get('location', '').lower().strip()
        
        if title and company:
            signature = f"{title}|{company}|{location}"
            self.job_signatures[signature] = job_data
            
    def get_duplicate_count(self) -> int:
        """
        Get the number of duplicate jobs detected
        
        Returns:
            Number of duplicates
        """
        # This is a simplified implementation
        # In practice, you'd track this during the deduplication process
        return 0
        
    def clear_cache(self):
        """Clear the deduplication cache"""
        self.seen_jobs.clear()
        self.job_signatures.clear()
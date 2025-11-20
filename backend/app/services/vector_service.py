"""
Vector embedding service for resume parsing
"""

import os
import logging
from typing import Dict, Any, List, Optional
from functools import wraps
import time

# Try to import vector libraries
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)

class VectorService:
    """Service for generating and storing vector embeddings"""
    
    def __init__(self):
        """Initialize vector service with configuration"""
        self.provider = os.getenv("VECTOR_PROVIDER", "openai").lower()
        self.model = os.getenv("VECTOR_MODEL", "text-embedding-ada-002")
        self.api_key = os.getenv("VECTOR_API_KEY")
        self.client = None
        self.local_model = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the vector client based on provider"""
        if self.provider == "openai" and openai:
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                logger.warning("OpenAI API key not provided, vector features disabled")
                self.client = None
        elif self.provider == "sentence-transformers" and SentenceTransformer:
            try:
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("SentenceTransformer model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer model: {str(e)}")
                self.local_model = None
        else:
            logger.warning(f"Unsupported vector provider: {self.provider} or missing dependencies")
            self.client = None
            self.local_model = None
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        try:
            if self.client:
                return self._generate_openai_embeddings(texts)
            elif self.local_model:
                return self._generate_local_embeddings(texts)
            else:
                logger.warning("No vector provider available, returning empty embeddings")
                return [[] for _ in texts]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return [[] for _ in texts]
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        if not self.client:
            return []
        
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        
        return [embedding.embedding for embedding in response.data]
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence transformer"""
        if not self.local_model:
            return []
        
        embeddings = self.local_model.encode(texts)
        return embeddings.tolist()
    
    def create_resume_vectors(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create vectors for resume components
        
        Args:
            parsed_data: Parsed resume data
            
        Returns:
            Dict with vector embeddings
        """
        vectors = {}
        
        # Create summary vector
        summary = parsed_data.get("summary", "")
        if summary:
            summary_vectors = self.generate_embeddings([summary])
            if summary_vectors and summary_vectors[0]:
                vectors["summary_vector"] = summary_vectors[0]
        
        # Create skills vector
        skills = parsed_data.get("skills", [])
        if skills:
            # Extract skill names and join them
            skill_names = [skill.get("skill", "") if isinstance(skill, dict) else str(skill) for skill in skills]
            skills_text = " ".join(skill_names)
            
            if skills_text:
                skills_vectors = self.generate_embeddings([skills_text])
                if skills_vectors and skills_vectors[0]:
                    vectors["skills_vector"] = skills_vectors[0]
        
        return vectors

# Global vector service instance
vector_service = VectorService()
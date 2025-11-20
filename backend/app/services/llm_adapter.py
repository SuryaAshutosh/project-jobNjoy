"""
LLM adapter for resume parsing refinement and normalization
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from functools import wraps
import time
from datetime import datetime

# Try to import OpenAI library
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

# Retry decorator for LLM calls
def retry_llm_call(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"LLM call failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"LLM attempt {attempts} failed: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator

class LLMAdapter:
    """Adapter for LLM services with pluggable backends"""
    
    def __init__(self):
        """Initialize LLM adapter with configuration"""
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.api_key = os.getenv("LLM_API_KEY")
        self.client = None
        
        # Rate limiting
        self.last_call_time = 0
        self.min_call_interval = float(os.getenv("LLM_MIN_CALL_INTERVAL", "1.0"))  # seconds
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        if self.provider == "openai" and openai:
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                logger.warning("OpenAI API key not provided, LLM features disabled")
                self.client = None
        else:
            logger.warning(f"Unsupported LLM provider: {self.provider} or missing dependencies")
            self.client = None
    
    def _rate_limit(self):
        """Enforce rate limiting between LLM calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    @retry_llm_call(max_attempts=3, delay=1, backoff=2)
    def normalize_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and refine parsed resume data using LLM
        
        Args:
            parsed_data: Raw parsed resume data
            
        Returns:
            Dict: Normalized and refined data
        """
        if not self.client:
            logger.warning("LLM client not available, returning original data")
            return parsed_data
        
        try:
            self._rate_limit()
            
            # Create prompt for LLM
            prompt = self._create_normalization_prompt(parsed_data)
            
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser that normalizes and refines resume data. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse response
            normalized_json = response.choices[0].message.content.strip()
            
            # Extract JSON from code block if present
            if normalized_json.startswith("```json"):
                normalized_json = normalized_json[7:]  # Remove ```json
            if normalized_json.endswith("```"):
                normalized_json = normalized_json[:-3]  # Remove ```
            
            normalized_data = json.loads(normalized_json)
            
            # Merge with original data to preserve any fields not handled by LLM
            merged_data = parsed_data.copy()
            merged_data.update(normalized_data)
            
            # Add provenance
            merged_data["provenance"] = merged_data.get("provenance", {})
            merged_data["provenance"]["llm_normalization"] = datetime.utcnow().isoformat()
            
            return merged_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            return parsed_data
        except Exception as e:
            logger.error(f"LLM normalization failed: {str(e)}")
            return parsed_data
    
    def _create_normalization_prompt(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create prompt for LLM normalization
        
        Args:
            parsed_data: Raw parsed resume data
            
        Returns:
            str: Formatted prompt
        """
        # Redact PII for logging
        redacted_data = self._redact_pii(parsed_data.copy())
        
        prompt = f"""
Please normalize and refine the following parsed resume data according to these requirements:

1. Clean ambiguous fields and standardize formats
2. Normalize dates to ISO-8601 format (YYYY-MM-DD)
3. Merge duplicate skills and canonicalize synonyms (e.g., "ReactJS" -> "React")
4. Generate a professional 2-3 sentence candidate summary
5. Return ONLY valid JSON without any markdown formatting

Input data:
{json.dumps(redacted_data, indent=2)}

Return the normalized JSON data with the same structure but improved formatting and consistency.
"""
        return prompt
    
    def _redact_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PII for safer logging and processing
        
        Args:
            data: Data to redact
            
        Returns:
            Dict: Redacted data
        """
        redacted = data.copy()
        
        # Redact emails
        if "emails" in redacted:
            redacted["emails"] = ["[REDACTED]" for _ in redacted["emails"]]
        
        # Redact phones
        if "phones" in redacted:
            redacted["phones"] = ["[REDACTED]" for _ in redacted["phones"]]
        
        # Redact name
        if "name" in redacted:
            redacted["name"] = "[REDACTED]"
        
        return redacted

# Global LLM adapter instance
llm_adapter = LLMAdapter()
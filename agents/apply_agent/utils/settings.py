"""
Settings loader for Auto-Apply Agent
"""

import os
import yaml
import json
import logging
from typing import Dict, Any

# Set up logger
logger = logging.getLogger(__name__)

class Settings:
    """Settings manager for the Auto-Apply Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize settings manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.settings = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Dict containing configuration settings
        """
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {self.config_path} not found, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values
        
        Returns:
            Dict containing default configuration settings
        """
        return {
            "backend": {
                "url": os.getenv("BACKEND_URL", "http://localhost:8000"),
                "agent_secret_key": os.getenv("AGENT_SECRET_KEY", "default-agent-secret")
            },
            "browser": {
                "headless": True,
                "slow_mo": 0,
                "timeout": 30000,
                "max_retries": 3,
                "stealth": True
            },
            "proxy": {
                "enabled": False,
                "urls": [],
                "username": "",
                "password": ""
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("LLM_API_KEY", ""),
                "temperature": 0.7,
                "max_tokens": 500
            },
            "sites": {},
            "field_mappings": {},
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "auto_apply_agent.log"
            },
            "retry": {
                "max_attempts": 3,
                "backoff_factor": 2,
                "jitter": True
            },
            "captcha": {
                "detection_keywords": [
                    "recaptcha",
                    "captcha",
                    "security check",
                    "verify you are human"
                ],
                "manual_review_required": True
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key
        
        Args:
            key: Configuration key (e.g., "backend.url")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key
        
        Args:
            key: Configuration key (e.g., "backend.url")
            value: Value to set
        """
        keys = key.split('.')
        config = self.settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        for key, value in updates.items():
            self.set(key, value)

# Global settings instance
settings = Settings()

# Load logging configuration
def setup_logging():
    """Set up logging based on configuration"""
    try:
        with open('logging.json', 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    except FileNotFoundError:
        # Fall back to basic logging configuration
        logging.basicConfig(
            level=settings.get("logging.level", "INFO"),
            format=settings.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logger.error(f"Error setting up logging: {e}")

# Initialize logging
setup_logging()
"""
Logging configuration for jobSee
"""

import logging
import sys
from typing import Union
import json
import os
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "exc_info", "exc_text", 
                          "stack_info", "getMessage"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)

def setup_logging(
    level: Union[int, str] = logging.INFO,
    json_format: bool = True,
    include_sentry: bool = False
) -> None:
    """
    Set up structured logging for the application
    
    Args:
        level: Logging level
        json_format: Whether to use JSON formatting
        include_sentry: Whether to include Sentry integration
    """
    # Create logger
    logger = logging.getLogger("jobsee")
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add Sentry integration if requested
    if include_sentry:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=os.getenv("SENTRY_DSN"),
                integrations=[sentry_logging],
                traces_sample_rate=1.0
            )
        except ImportError:
            logger.warning("Sentry SDK not installed, skipping Sentry integration")

# Configure root logger
setup_logging()

# Create a logger instance for use in the application
app_logger = logging.getLogger("jobsee")

# Example usage:
# app_logger.info("Application started", extra={"version": "1.0.0"})
# app_logger.error("An error occurred", extra={"error_code": 500})

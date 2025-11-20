"""
Custom exception handlers for JobBuddy
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

# Set up logger
logger = logging.getLogger("jobbuddy")

class JobBuddyException(Exception):
    """Base exception class for JobBuddy"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundException(JobBuddyException):
    """Raised when a user is not found"""
    def __init__(self, user_id: str):
        super().__init__(f"User with ID {user_id} not found", 404)

class UnauthorizedException(JobBuddyException):
    """Raised when a user is not authorized"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)

class ForbiddenException(JobBuddyException):
    """Raised when access is forbidden"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)

class InvalidCredentialsException(JobBuddyException):
    """Raised when credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid credentials", 401)

class FileTooLargeException(JobBuddyException):
    """Raised when an uploaded file is too large"""
    def __init__(self, max_size: int):
        super().__init__(f"File too large. Maximum size is {max_size} bytes", 400)

class InvalidFileTypeException(JobBuddyException):
    """Raised when an uploaded file has an invalid type"""
    def __init__(self, allowed_types: list):
        super().__init__(f"Invalid file type. Allowed types: {', '.join(allowed_types)}", 400)

# Exception handlers
async def jobbuddy_exception_handler(request: Request, exc: JobBuddyException):
    """Handle JobBuddy custom exceptions"""
    logger.error(f"JobBuddy exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation exceptions"""
    logger.error(f"Validation exception: {str(exc)}", extra={
        "status_code": 422,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"General exception: {str(exc)}", extra={
        "status_code": 500,
        "path": request.url.path,
        "method": request.method
    }, exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Exception handler registration
exception_handlers = {
    JobBuddyException: jobbuddy_exception_handler,
    HTTPException: http_exception_handler,
    Exception: general_exception_handler,
}
"""
Security middleware for JobBuddy
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import uuid

def add_security_headers(app: FastAPI):
    """
    Add security headers to the application
    
    Args:
        app: The FastAPI application
    """
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response: Response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add a request ID for tracking
        request_id = str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id
        
        return response

def configure_cors(app: FastAPI):
    """
    Configure CORS for the application
    
    Args:
        app: The FastAPI application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        allow_origin_regex="https?://(localhost|127\.0\.0\.1|172\.28\.0\.1|192\.168\.29\.203):(3000|3001|3002|8000)",
    )
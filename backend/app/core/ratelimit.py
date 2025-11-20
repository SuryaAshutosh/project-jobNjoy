"""
Rate limiting middleware for JobBuddy
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.dep import RateLimiter
import redis.asyncio as redis
from app.core.config import settings

async def init_rate_limiter(app: FastAPI):
    """
    Initialize the rate limiter
    
    Args:
        app: The FastAPI application
    """
    # Initialize Redis connection
    redis_connection = redis.from_url(settings.REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(redis_connection)

def add_rate_limiting(app: FastAPI):
    """
    Add rate limiting to the application
    
    Args:
        app: The FastAPI application
    """
    # Add global rate limiting middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # This is a simplified example
        # In a real implementation, you would use the FastAPILimiter decorators
        # on specific endpoints or implement more sophisticated rate limiting
        response = await call_next(request)
        return response

# Example of how to apply rate limiting to specific endpoints:
# 
# @router.get("/jobs/")
# @RateLimiter(times=10, minutes=1)  # 10 requests per minute
# async def list_jobs(...):
#     ...
#
# @router.post("/auth/login")
# @RateLimiter(times=5, minutes=1)  # 5 login attempts per minute
# async def login_user(...):
#     ...
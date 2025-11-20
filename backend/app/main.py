from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, resume, jobs, applications, agents, payments, dashboard
from app.core.config import settings
from app.core.db_init import create_database_tables
from app.core.exceptions import exception_handlers
from app.core.ratelimit import init_rate_limiter
from app.core.security import add_security_headers, configure_cors
from datetime import datetime

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    exception_handlers=exception_handlers
)

# Configure CORS and security headers
configure_cors(app)
add_security_headers(app)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.on_event("startup")
async def startup_event():
    create_database_tables()
    await init_rate_limiter(app)

@app.get("/")
async def root():
    return {"message": "Welcome to JobBuddy API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "jobbuddy-backend"
    }
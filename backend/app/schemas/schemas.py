from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import json

# Enums for consistency
from ..models.db_models import UserRole, SubscriptionStatus, ApplicationStatus

# -----------------------------------------------------
# USER SCHEMAS
# -----------------------------------------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    role: UserRole
    subscription_status: SubscriptionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# -----------------------------------------------------
# RESUME SCHEMAS
# -----------------------------------------------------

class ResumeBase(BaseModel):
    file_url: str
    raw_text: str
    parsed_data: Optional[Dict[str, Any]] = None

class ResumeUpload(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# -----------------------------------------------------
# JOB SOURCE SCHEMAS
# -----------------------------------------------------

class JobSourceBase(BaseModel):
    name: str
    base_url: str

class JobSourceCreate(JobSourceBase):
    pass

class JobSourceResponse(JobSourceBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# -----------------------------------------------------
# JOB SCHEMAS
# -----------------------------------------------------

class JobBase(BaseModel):
    title: str
    company: str
    url: str
    description: str
    skills: Optional[List[str]] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None

class JobCreate(JobBase):
    source_id: UUID

class JobResponse(JobBase):
    id: UUID
    source_id: UUID
    created_at: datetime
    # Adding relationship data for better frontend integration
    source: Optional[JobSourceResponse] = None

    class Config:
        orm_mode = True

# -----------------------------------------------------
# APPLICATION SCHEMAS
# -----------------------------------------------------

class ApplicationBase(BaseModel):
    job_id: UUID
    status: ApplicationStatus = ApplicationStatus.PENDING
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: UUID
    user_id: UUID
    applied_at: Optional[datetime] = None
    created_at: datetime
    # Adding relationship data for better frontend integration
    job: Optional[JobResponse] = None

    class Config:
        orm_mode = True

# -----------------------------------------------------
# AI LOG SCHEMAS
# -----------------------------------------------------

class AILogBase(BaseModel):
    action: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None

class AILogCreate(AILogBase):
    pass

class AILogResponse(AILogBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# -----------------------------------------------------
# BILLING SCHEMAS
# -----------------------------------------------------

class BillingBase(BaseModel):
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

class BillingCreate(BillingBase):
    user_id: UUID

class BillingUpdate(BillingBase):
    pass

class BillingResponse(BillingBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
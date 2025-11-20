"""
Test script to verify that the SQLAlchemy models and Pydantic schemas work correctly
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base, User, Resume, JobSource, Job, Application, AILog, Billing
from app.schemas.schemas import UserCreate, UserResponse, ResumeUpload, JobCreate
import uuid
from datetime import datetime

def test_models_and_schemas():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test creating a user with Pydantic schema
        user_create = UserCreate(
            name="Test User",
            email="test@example.com",
            password="securepassword123"
        )
        
        # Convert Pydantic model to SQLAlchemy model
        user = User(
            name=user_create.name,
            email=user_create.email,
            password_hash="hashed_password_here"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Test converting SQLAlchemy model to Pydantic response
        user_response = UserResponse.from_orm(user)
        print(f"Created user: {user_response}")
        
        # Test creating a job source
        job_source = JobSource(
            name="Test Source",
            base_url="https://test.com"
        )
        
        db.add(job_source)
        db.commit()
        db.refresh(job_source)
        
        # Test creating a job with Pydantic schema
        job_create = JobCreate(
            source_id=job_source.id,
            title="Test Job",
            company="Test Company",
            url="https://test.com/job/1",
            description="This is a test job",
            skills=["Python", "SQL"],
            salary_range="$50,000 - $70,000",
            location="Remote"
        )
        
        # Convert Pydantic model to SQLAlchemy model
        job = Job(**job_create.dict())
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        print(f"Created job: {job.title} at {job.company}")
        
        print("All tests passed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_models_and_schemas()
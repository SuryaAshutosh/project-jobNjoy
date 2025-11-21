"""
Seed script for jobSee database
Populates the database with sample data for development and testing
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

from ..models.db_models import (
    Base, User, Resume, JobSource, Job, Application, AILog, Billing,
    UserRole, SubscriptionStatus, ApplicationStatus
)

# Database connection configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://jobsee:jobsee@localhost:5432/jobsee"
)

def seed_database():
    """Seed the database with sample data"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing data
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Create demo users
        user1_id = uuid.uuid4()
        user1 = User(
            id=user1_id,
            name="John Doe",
            email="john.doe@example.com",
            password_hash="$2b$12$Lq4sJKAynpu2BVPexksc.uOi.lEwvFJhugSqcsmDqMWoiWwcQaX5G",  # bcrypt hash for "password123"
            role=UserRole.USER,
            subscription_status=SubscriptionStatus.PRO
        )
        
        user2_id = uuid.uuid4()
        user2 = User(
            id=user2_id,
            name="Jane Smith",
            email="jane.smith@example.com",
            password_hash="$2b$12$Lq4sJKAynpu2BVPexksc.uOi.lEwvFJhugSqcsmDqMWoiWwcQaX5G",  # bcrypt hash for "password123"
            role=UserRole.ADMIN,
            subscription_status=SubscriptionStatus.UNLIMITED
        )
        
        db.add(user1)
        db.add(user2)
        db.commit()
        
        # Create resumes for users
        resume1 = Resume(
            user_id=user1_id,
            file_url="https://storage.example.com/resumes/john_doe_resume.pdf",
            raw_text="Experienced software engineer with 5 years in Python and JavaScript...",
            parsed_data={
                "skills": ["Python", "JavaScript", "SQL"],
                "experience_years": 5
            }
        )
        
        resume2 = Resume(
            user_id=user2_id,
            file_url="https://storage.example.com/resumes/jane_smith_resume.pdf",
            raw_text="Senior data scientist with expertise in machine learning and AI...",
            parsed_data={
                "skills": ["Python", "Machine Learning", "TensorFlow"],
                "experience_years": 8
            }
        )
        
        db.add(resume1)
        db.add(resume2)
        db.commit()
        
        # Create job sources
        source1_id = uuid.uuid4()
        source1 = JobSource(
            id=source1_id,
            name="LinkedIn",
            base_url="https://linkedin.com/jobs"
        )
        
        source2_id = uuid.uuid4()
        source2 = JobSource(
            id=source2_id,
            name="Indeed",
            base_url="https://indeed.com"
        )
        
        source3_id = uuid.uuid4()
        source3 = JobSource(
            id=source3_id,
            name="Glassdoor",
            base_url="https://glassdoor.com"
        )
        
        db.add(source1)
        db.add(source2)
        db.add(source3)
        db.commit()
        
        # Create jobs
        job1_id = uuid.uuid4()
        job1 = Job(
            id=job1_id,
            source_id=source1_id,
            title="Senior Python Developer",
            company="Tech Corp",
            url="https://linkedin.com/jobs/view/12345",
            description="We are looking for an experienced Python developer...",
            skills=["Python", "Django", "REST API"],
            salary_range="$90,000 - $120,000",
            location="San Francisco, CA"
        )
        
        job2_id = uuid.uuid4()
        job2 = Job(
            id=job2_id,
            source_id=source1_id,
            title="Frontend Engineer",
            company="Design Studio",
            url="https://linkedin.com/jobs/view/12346",
            description="Join our team to build beautiful user interfaces...",
            skills=["React", "JavaScript", "CSS"],
            salary_range="$80,000 - $110,000",
            location="Remote"
        )
        
        job3_id = uuid.uuid4()
        job3 = Job(
            id=job3_id,
            source_id=source2_id,
            title="Data Scientist",
            company="Analytics Inc",
            url="https://indeed.com/view/7890",
            description="Seeking a data scientist to analyze large datasets...",
            skills=["Python", "Machine Learning", "SQL"],
            salary_range="$100,000 - $140,000",
            location="New York, NY"
        )
        
        job4_id = uuid.uuid4()
        job4 = Job(
            id=job4_id,
            source_id=source2_id,
            title="DevOps Engineer",
            company="Cloud Systems",
            url="https://indeed.com/view/7891",
            description="Help us build and maintain our cloud infrastructure...",
            skills=["AWS", "Docker", "Kubernetes"],
            salary_range="$110,000 - $150,000",
            location="Austin, TX"
        )
        
        job5_id = uuid.uuid4()
        job5 = Job(
            id=job5_id,
            source_id=source3_id,
            title="Product Manager",
            company="Innovate Co",
            url="https://glassdoor.com/listing/5555",
            description="Lead product development for our flagship application...",
            skills=["Product Strategy", "Agile", "User Research"],
            salary_range="$120,000 - $160,000",
            location="Seattle, WA"
        )
        
        db.add(job1)
        db.add(job2)
        db.add(job3)
        db.add(job4)
        db.add(job5)
        db.commit()
        
        # Create applications
        application1 = Application(
            user_id=user1_id,
            job_id=job1_id,
            status=ApplicationStatus.APPLIED,
            applied_at=datetime.utcnow() - timedelta(days=5),
            notes="Applied through company website"
        )
        
        application2 = Application(
            user_id=user1_id,
            job_id=job3_id,
            status=ApplicationStatus.PENDING,
            notes="Preparing cover letter"
        )
        
        db.add(application1)
        db.add(application2)
        db.commit()
        
        # Create AI logs
        ai_log1 = AILog(
            user_id=user1_id,
            action="resume_parsing",
            input_data={"resume_id": str(resume1.id)},
            output_data={"status": "success", "parsed_sections": 5}
        )
        
        ai_log2 = AILog(
            user_id=user2_id,
            action="job_matching",
            input_data={"resume_id": str(resume2.id), "job_id": str(job3_id)},
            output_data={"match_score": 0.87, "recommended": True}
        )
        
        db.add(ai_log1)
        db.add(ai_log2)
        db.commit()
        
        # Create billing records
        billing1 = Billing(
            user_id=user1_id,
            stripe_customer_id="cus_JohnDoe123",
            stripe_subscription_id="sub_JohnDoe123",
            plan="pro",
            status="active",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        billing2 = Billing(
            user_id=user2_id,
            stripe_customer_id="cus_JaneSmith456",
            stripe_subscription_id="sub_JaneSmith456",
            plan="unlimited",
            status="active",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(billing1)
        db.add(billing2)
        db.commit()
        
        print("Database seeded successfully with sample data!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
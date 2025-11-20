"""
Database initialization script for JobBuddy
Creates all tables and provides utility functions for database setup
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..models.db_models import Base
import os

# Database connection configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://jobbuddy_user:jobbuddy_pass@localhost:5432/jobbuddy_db"
)

def create_database_tables():
    """Create all database tables"""
    engine = create_engine(DATABASE_URL)
    
    # Enable UUID extension for PostgreSQL
    with engine.connect() as conn:
        try:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not enable UUID extension: {e}")
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db_session():
    """Create and return a database session"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == "__main__":
    create_database_tables()
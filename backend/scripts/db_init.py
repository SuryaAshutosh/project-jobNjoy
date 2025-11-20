"""
Database initialization script for JobBuddy
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from app.db import init_db
from app.core.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_url = settings.DATABASE_URL
    db_name = db_url.split('/')[-1]
    
    # Create connection to PostgreSQL without specifying database
    admin_url = '/'.join(db_url.split('/')[:-1]) + '/postgres'
    engine = create_engine(admin_url)
    
    # Check if database exists
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        exists = result.fetchone()
        
        if not exists:
            # Create database
            conn.execute(text("COMMIT"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database {db_name} created successfully")
        else:
            print(f"Database {db_name} already exists")

def init_database():
    """Initialize the database tables"""
    try:
        init_db()
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def create_extensions():
    """Create required PostgreSQL extensions"""
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
            print("UUID extension created successfully")
        except Exception as e:
            print(f"Warning: Could not create UUID extension: {e}")

if __name__ == "__main__":
    print("Initializing JobBuddy database...")
    
    # Create database
    create_database()
    
    # Create extensions
    create_extensions()
    
    # Initialize tables
    init_database()
    
    print("Database initialization completed!")
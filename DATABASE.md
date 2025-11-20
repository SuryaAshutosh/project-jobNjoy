# JobBuddy Database Implementation

This document provides a comprehensive overview of the database implementation for the JobBuddy platform.

## 1. DATABASE SCHEMA (DDL SQL)

The database schema is defined in `infra/postgres/schema.sql`. It includes the following tables:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    subscription_status VARCHAR(50) NOT NULL DEFAULT 'free',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### Resumes Table
```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    parsed_data JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### Job Sources Table
```sql
CREATE TABLE job_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    base_url TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES job_sources(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    description TEXT NOT NULL,
    skills TEXT[],
    salary_range VARCHAR(100),
    location VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### Applications Table
```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    applied_at TIMESTAMP WITHOUT TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### AI Logs Table
```sql
CREATE TABLE ai_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

### Billing Table
```sql
CREATE TABLE billing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    plan VARCHAR(100),
    status VARCHAR(100),
    current_period_end TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

## 2. SQLALCHEMY MODELS

The SQLAlchemy models are implemented in `backend/app/models/db_models.py`. Key features include:

- UUID primary keys for all tables
- Proper foreign key relationships with `back_populates` for bidirectional relationships
- Indexes on frequently queried columns
- Enum types for status fields
- `__repr__` methods for debugging
- Cascade delete operations where appropriate

## 3. Pydantic Schemas

Pydantic schemas in `backend/app/schemas/schemas.py` provide validation and serialization layers:

- Separate schemas for create, update, and response operations
- Type hints for all fields
- Validators for data validation (e.g., password strength)
- Nested models for complex data structures
- ORM mode enabled for easy conversion from SQLAlchemy models

## 4. ER DIAGRAM DESCRIPTION

See `ARCHITECTURE.md` for the complete ER diagram description showing entities, relationships, and cardinality.

## 5. Database Initialization Script

The initialization script in `backend/app/core/db_init.py`:

- Creates all database tables
- Handles PostgreSQL UUID extension setup
- Provides a session factory for database connections

## 6. Seed Script

The seed script in `backend/app/core/seed.py` populates the database with sample data:

- 2 demo users (one regular, one admin)
- 3 job sources (LinkedIn, Indeed, Glassdoor)
- 5 jobs across different sources
- 2 applications
- Sample AI logs and billing records

## Running the Database Components

1. Ensure PostgreSQL is running and configured properly
2. Set the DATABASE_URL environment variable
3. Run the initialization script:
   ```bash
   cd backend
   python -m app.core.db_init
   ```
4. To seed the database with sample data:
   ```bash
   python -m app.core.seed
   ```

## Testing

Run the test script to verify models and schemas work correctly:
```bash
cd backend
python -m app.core.test_models
```
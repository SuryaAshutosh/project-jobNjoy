# JobBuddy Architecture

## Database Components

The JobBuddy platform uses PostgreSQL as its primary database with SQLAlchemy ORM for database operations.

### Key Components

1. **Database Schema** - Defined in `infra/postgres/schema.sql`
2. **SQLAlchemy Models** - Located in `backend/app/models/db_models.py`
3. **Pydantic Schemas** - Located in `backend/app/schemas/schemas.py`
4. **Database Initialization** - Script in `backend/app/core/db_init.py`
5. **Database Seeding** - Script in `backend/app/core/seed.py`

## Entity Relationship Diagram

### Entities and Their Attributes

1. **Users**
   - id (UUID, PK)
   - name (String)
   - email (String, Unique)
   - password_hash (String)
   - role (Enum: user, admin)
   - subscription_status (Enum: free, basic, pro, unlimited)
   - created_at (DateTime)
   - updated_at (DateTime)

2. **Resumes**
   - id (UUID, PK)
   - user_id (UUID, FK to Users.id)
   - file_url (String)
   - raw_text (Text)
   - parsed_data (JSONB)
   - created_at (DateTime)

3. **Job_Sources**
   - id (UUID, PK)
   - name (String)
   - base_url (String)
   - created_at (DateTime)

4. **Jobs**
   - id (UUID, PK)
   - source_id (UUID, FK to Job_Sources.id)
   - title (String)
   - company (String)
   - url (String)
   - description (Text)
   - skills (Array of Strings)
   - salary_range (String)
   - location (String)
   - created_at (DateTime)

5. **Applications**
   - id (UUID, PK)
   - user_id (UUID, FK to Users.id)
   - job_id (UUID, FK to Jobs.id)
   - status (Enum: pending, applied, failed, skipped)
   - applied_at (DateTime)
   - notes (Text)
   - created_at (DateTime)

6. **AI_Logs**
   - id (UUID, PK)
   - user_id (UUID, FK to Users.id)
   - action (String)
   - input_data (JSONB)
   - output_data (JSONB)
   - created_at (DateTime)

7. **Billing**
   - id (UUID, PK)
   - user_id (UUID, FK to Users.id, Unique)
   - stripe_customer_id (String)
   - stripe_subscription_id (String)
   - plan (String)
   - status (String)
   - current_period_end (DateTime)
   - created_at (DateTime)

### Relationships and Cardinality

1. **Users ↔ Resumes**
   - One-to-Many (1:N)
   - One user can have multiple resumes
   - Each resume belongs to exactly one user

2. **Users ↔ Applications**
   - One-to-Many (1:N)
   - One user can have multiple applications
   - Each application belongs to exactly one user

3. **Users ↔ AI_Logs**
   - One-to-Many (1:N)
   - One user can have multiple AI logs
   - Each AI log belongs to exactly one user

4. **Users ↔ Billing**
   - One-to-One (1:1)
   - Each user has exactly one billing record
   - Each billing record belongs to exactly one user

5. **Job_Sources ↔ Jobs**
   - One-to-Many (1:N)
   - One job source can have multiple jobs
   - Each job belongs to exactly one job source

6. **Jobs ↔ Applications**
   - One-to-Many (1:N)
   - One job can have multiple applications
   - Each application is for exactly one job

### Visual Representation

```
Users ||--o{ Resumes
Users ||--o{ Applications
Users ||--o{ AI_Logs
Users }|--|| Billing
Job_Sources ||--o{ Jobs
Jobs ||--o{ Applications
```

Where:
- `||` represents exactly one
- `o{` represents zero or more
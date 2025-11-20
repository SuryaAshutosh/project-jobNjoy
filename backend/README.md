# JobBuddy Backend

JobBuddy is a comprehensive job application automation platform built with FastAPI, PostgreSQL, and modern Python practices.

## Features

- **User Authentication**: JWT-based authentication with password hashing
- **Resume Management**: Upload, parse, and store resumes in multiple formats
- **Job Scraping**: Automated job scraping from multiple sources
- **Auto-Apply**: Automated job application workflow
- **Agent Integration**: Communication with Qoder agents
- **Payment Processing**: Stripe integration for subscriptions
- **Dashboard**: Statistics and metrics for users
- **Background Tasks**: Celery for long-running operations
- **File Storage**: S3/MinIO compatible storage
- **Structured Logging**: JSON logging with optional Sentry integration

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routers
│   ├── core/             # Core utilities (auth, config, storage, tasks)
│   ├── crud/             # Database CRUD operations
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic services
│   ├── db.py             # Database connection
│   ├── logging_config.py # Logging configuration
│   └── main.py           # FastAPI application
├── scripts/              # Utility scripts
├── tests/                # Unit tests
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL (if not using Docker)

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# Database
DATABASE_URL=postgresql://jobbuddy:jobbuddy_pass@localhost:5432/jobbuddy

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# File Storage (S3/MinIO)
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=jobbuddy-resumes

# Agent Communication
AGENT_SECRET_KEY=your-agent-secret-key-here-change-in-production
```

### Running with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Initialize the database
docker-compose exec app python scripts/db_init.py
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the database
python scripts/db_init.py

# Start the development server
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/redoc - Alternative API documentation (ReDoc)

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Key Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user profile

### Resume Management
- `POST /api/resume/upload` - Upload a resume
- `POST /api/resume/{id}/parse` - Parse a resume
- `GET /api/resume/{id}` - Get a resume
- `GET /api/resume/` - List resumes

### Jobs
- `GET /api/jobs/` - List jobs
- `GET /api/jobs/{id}` - Get a job
- `POST /api/jobs/scrape` - Trigger job scraping (admin only)
- `POST /api/jobs/import` - Import jobs from agent (admin only)

### Applications
- `POST /api/applications/` - Create a job application
- `POST /api/applications/{id}/auto-apply` - Start auto-apply workflow
- `POST /api/applications/agent-result` - Receive agent results
- `GET /api/applications/` - List applications

### Agents
- `POST /api/agents/register-run` - Register agent run
- `POST /api/agents/update-run-status` - Update agent run status
- `POST /api/agents/trigger-workflow` - Trigger agent workflow
- `POST /api/agents/webhook` - Receive agent notifications

### Payments
- `POST /api/payments/create-checkout-session` - Create Stripe checkout session
- `POST /api/payments/webhook` - Handle Stripe webhooks
- `GET /api/payments/plans` - List subscription plans

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/applications/chart` - Get applications chart data
- `GET /api/dashboard/recent-activity` - Get recent activity

## Background Tasks

The application uses Celery for background tasks:
- Resume parsing
- Job scraping
- Auto-apply workflows

To start the Celery worker:
```bash
celery -A app.core.tasks.celery_app worker --loglevel=info
```

To start the Celery beat scheduler:
```bash
celery -A app.core.tasks.celery_app beat --loglevel=info
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- File type and size validation
- Agent signature verification
- Stripe webhook signature verification
- CORS protection
- Rate limiting (via fastapi-limiter)

## Monitoring and Logging

- Structured JSON logging
- Sentry integration (optional)
- Health check endpoint at `GET /health`

## Deployment

### Docker Deployment

```bash
# Build the Docker image
docker build -t jobbuddy .

# Run the container
docker run -p 8000:8000 jobbuddy
```

### Production Considerations

1. Use a production-grade database (PostgreSQL with connection pooling)
2. Use a production-grade message broker (Redis with persistence)
3. Use a production-grade file storage (AWS S3, Google Cloud Storage)
4. Set strong secret keys
5. Enable HTTPS
6. Configure proper logging and monitoring
7. Set up automated backups
8. Implement proper error handling and retry mechanisms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Run tests and linting
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
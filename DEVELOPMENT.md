# JobBuddy Development Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

## Initial Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd JobBuddy
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Configure environment variables:
   ```bash
   cp infra/.env.example infra/.env
   # Edit infra/.env with your configuration
   ```

## Development Workflow

### Running Services Locally

#### Option 1: Using Docker Compose (Recommended for full stack testing)
```bash
cd infra
docker-compose up -d
```

This will start all services:
- PostgreSQL database
- Redis cache
- Backend API
- Frontend application
- Nginx reverse proxy

#### Option 2: Running services individually (Recommended for development)

##### Backend Development
```bash
cd backend
# Install dependencies (if not already done)
pip install -r requirements.txt
# Run development server
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

##### Frontend Development
```bash
cd frontend
# Install dependencies (if not already done)
npm install
# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Database Migrations

To create and run database migrations:
```bash
cd backend
# Create a new migration
alembic revision --autogenerate -m "Migration message"
# Apply migrations
alembic upgrade head
```

### Testing

#### Backend Testing
```bash
cd backend
pytest
```

#### Frontend Testing
```bash
cd frontend
npm run test
```

## Project Structure

### Backend
- `app/main.py`: Application entry point
- `app/api/`: API route definitions
- `app/core/`: Core configurations and security
- `app/models/`: Database models
- `app/schemas/`: Pydantic schemas for validation
- `app/crud/`: Database operations
- `app/utils/`: Utility functions

### Frontend
- `src/App.tsx`: Main application component
- `src/main.tsx`: Entry point
- `src/components/`: Reusable UI components
- `src/pages/`: Page components
- `src/hooks/`: Custom React hooks
- `src/services/`: API service clients
- `src/store/`: State management

### Chrome Extension
- `manifest.json`: Extension configuration
- `popup/`: Extension popup UI
- `content-scripts/`: Scripts injected into web pages
- `background/`: Background service workers

### Agents
- `scraper_agent/`: Job scraping workflows
- `apply_agent/`: Auto-application workflows

## API Development

The backend uses FastAPI, which automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Key environment variables are defined in `infra/.env`:
- `POSTGRES_*`: Database configuration
- `SECRET_KEY`: Application secret key
- `STRIPE_*`: Stripe API keys
- `VITE_API_URL`: Frontend API URL

## Deployment

### Development Deployment
```bash
cd infra
docker-compose up -d
```

### Production Deployment
For production deployment, see `infra/kubernetes/` for Kubernetes manifests or use a cloud platform like AWS ECS, Google Cloud Run, or Azure Container Instances.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Run the test suite
6. Commit your changes
7. Push to the branch
8. Create a pull request

## Troubleshooting

### Common Issues

1. **Port already in use**: Stop existing containers with `docker-compose down`
2. **Database connection errors**: Ensure PostgreSQL is running and credentials are correct
3. **Frontend not connecting to backend**: Check API_URL in environment variables
4. **Permission denied errors**: Ensure proper file permissions on scripts

### Useful Commands

```bash
# View logs
docker-compose logs <service-name>

# Restart a specific service
docker-compose restart <service-name>

# Access database shell
docker-compose exec db psql -U jobbuddy jobbuddy

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh
```

## Code Quality

### Backend
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused

### Frontend
- Follow TypeScript best practices
- Use functional components with hooks
- Keep components small and focused
- Use meaningful variable and function names

## Security Best Practices

- Never commit sensitive information to version control
- Use environment variables for configuration
- Validate and sanitize all user input
- Keep dependencies up to date
- Use HTTPS in production
- Implement proper authentication and authorization

This guide should help you get started with developing JobBuddy. For any questions or issues, please refer to the architecture documentation or reach out to the team.
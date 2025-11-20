#!/bin/bash

# JobBuddy Smoke Test Script
# Tests all critical components of the platform

set -e  # Exit on any error

echo "=========================================="
echo " JobBuddy Platform Smoke Test"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a logs/smoke/full_smoke_test.log
}

log_with_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}" | tee -a logs/smoke/full_smoke_test.log
    else
        echo -e "${RED}✗ $1${NC}" | tee -a logs/smoke/full_smoke_test.log
        exit 1
    fi
}

# Create log directory if it doesn't exist
mkdir -p logs/smoke

# Start timing
START_TIME=$(date +%s)

# 1. Start docker-compose services
log "Starting docker-compose services..."
docker-compose -f infra/docker-compose.yml up -d
log_with_status "Docker services started" $?

# 2. Wait for services to be ready
log "Waiting for services to be ready..."

# Wait for database
until docker-compose -f infra/docker-compose.yml exec db pg_isready > /dev/null 2>&1
do
    sleep 1
done
log_with_status "Database is ready" $?

# Wait for backend
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        BACKEND_READY=true
        break
    fi
    sleep 2
done

if [ "$BACKEND_READY" = true ]; then
    log_with_status "Backend is ready" 0
else
    log_with_status "Backend failed to start" 1
fi

# 3. Run Alembic migrations
log "Running database migrations..."
docker-compose -f infra/docker-compose.yml exec backend alembic upgrade head
log_with_status "Database migrations completed" $?

# 4. Run backend unit tests
log "Running backend unit tests..."
docker-compose -f infra/docker-compose.yml exec backend pytest -v
log_with_status "Backend unit tests passed" $?

# 5. Run frontend tests
log "Running frontend tests..."
cd frontend && npm test -- --run
TEST_RESULT=$?
cd ..
log_with_status "Frontend tests completed" $TEST_RESULT

# 6. API Tests
log "Starting API tests..."

# a) Health check
log "Testing GET /health..."
curl -s -f http://localhost:8000/health > /dev/null
log_with_status "Health check passed" $?

# b) Register user
log "Testing POST /auth/register..."
REGISTER_RESPONSE=$(curl -s -f -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "smoketest@example.com", "password": "SmokeTestPass123!", "full_name": "Smoke Test User"}')
log_with_status "User registration passed" $?

# Extract user ID for cleanup
USER_ID=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# c) Login and get token
log "Testing POST /auth/login..."
LOGIN_RESPONSE=$(curl -s -f -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=smoketest@example.com&password=SmokeTestPass123!")
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
log_with_status "User login passed" $?

# d) Get user profile
log "Testing GET /auth/me..."
curl -s -f -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
log_with_status "User profile retrieval passed" $?

# e) Upload sample resume
log "Testing resume upload..."
# Create a simple text file as sample resume
echo "John Doe
Software Engineer
Experience: 5 years in Python, JavaScript
Education: BS Computer Science" > /tmp/sample_resume.txt

UPLOAD_RESPONSE=$(curl -s -f -X POST http://localhost:8000/api/resume/upload \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@/tmp/sample_resume.txt")
RESUME_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
log_with_status "Resume upload passed" $?

# f) Trigger resume parsing
log "Testing resume parsing..."
curl -s -f -X POST http://localhost:8000/api/resume/$RESUME_ID/parse \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"background": false}' > /dev/null
log_with_status "Resume parsing passed" $?

# g) Import sample job
log "Testing job import..."
JOB_IMPORT_DATA='[
  {
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "description": "We are looking for a senior software engineer...",
    "url": "https://techcorp.com/jobs/123",
    "salary": "$120,000 - $150,000",
    "source_id": "smoke_test_source"
  }
]'
curl -s -f -X POST http://localhost:8000/api/jobs/import \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$JOB_IMPORT_DATA" > /dev/null
log_with_status "Job import passed" $?

# h) Get jobs list
log "Testing GET /jobs..."
curl -s -f -X GET http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
log_with_status "Jobs listing passed" $?

# i) Create application
log "Testing application creation..."
APPLICATION_DATA='{
  "job_id": "1",
  "resume_id": "'$RESUME_ID'",
  "cover_letter": "I am excited to apply for this position..."
}'
APPLICATION_RESPONSE=$(curl -s -f -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$APPLICATION_DATA")
APPLICATION_ID=$(echo $APPLICATION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
log_with_status "Application creation passed" $?

# j) Simulate agent callback
log "Testing agent callback..."
curl -s -f -X POST "http://localhost:8000/api/applications/agent-result?application_id=$APPLICATION_ID&status=SUBMITTED&notes=Application%20submitted%20by%20agent" \
  -H "Content-Type: application/json" \
  -H "X-Signature: test_signature" > /dev/null
log_with_status "Agent callback passed" $?

# k) Mock Stripe webhook event
log "Testing Stripe webhook..."
STRIPE_EVENT='{
  "id": "evt_123456789",
  "object": "event",
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_123456789",
      "object": "checkout.session",
      "customer": "cus_123456789",
      "client_reference_id": "'$USER_ID'",
      "mode": "subscription",
      "payment_status": "paid",
      "subscription": "sub_123456789"
    }
  }
}'
curl -s -f -X POST http://localhost:8000/api/payments/webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test_signature" \
  -d "$STRIPE_EVENT" > /dev/null
log_with_status "Stripe webhook test passed" $?

# Clean up temporary file
rm -f /tmp/sample_resume.txt

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo " Smoke Test Summary"
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "Total time: ${DURATION} seconds"
echo "Log file: logs/smoke/full_smoke_test.log"
echo ""
echo "READY FOR DEPLOYMENT"
echo ""

exit 0
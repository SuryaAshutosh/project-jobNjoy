#!/bin/bash

# JobBuddy API curl examples

# Base URL
BASE_URL="http://localhost:8000/api"

# 1. Register a new user
echo "1. Register a new user"
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

echo -e "\n"

# 2. Login and get access token
echo "2. Login and get access token"
LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=john@example.com&password=securepassword123')

echo $LOGIN_RESPONSE

# Extract access token (you would parse this in a real script)
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

echo -e "\n"

# 3. Get current user profile
echo "3. Get current user profile"
curl -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo -e "\n"

# 4. Upload a resume (you need to have a test.pdf file)
echo "4. Upload a resume"
curl -X POST "$BASE_URL/resume/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@test.pdf"

echo -e "\n"

# 5. List jobs
echo "5. List jobs"
curl -X GET "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo -e "\n"

# 6. Get dashboard stats
echo "6. Get dashboard stats"
curl -X GET "$BASE_URL/dashboard/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo -e "\n"

# 7. Create a Stripe checkout session
echo "7. Create a Stripe checkout session"
curl -X POST "$BASE_URL/payments/create-checkout-session" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "pro",
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel"
  }'

echo -e "\n"

# 8. Trigger job scraping (admin only)
echo "8. Trigger job scraping (admin only)"
curl -X POST "$BASE_URL/jobs/scrape?source_id=123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo -e "\n"

# 9. Agent authentication example
echo "9. Agent authentication example"
curl -X POST "$BASE_URL/agents/register-run?agent_id=scraper-001" \
  -H "Content-Type: application/json" \
  -H "X-Signature: your-generated-signature" \
  -d '{
    "run_data": {
      "source": "linkedin",
      "job_count": 50
    }
  }'
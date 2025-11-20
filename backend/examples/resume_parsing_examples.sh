#!/bin/bash

# Resume Parsing Service - Example Usage

# Set variables
BASE_URL="http://localhost:8000/api/v1"
TOKEN="your-jwt-token-here"

echo "=== Resume Parsing Service Examples ==="

# 1. Upload a resume
echo "1. Uploading resume..."
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/resume/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@sample_resume.pdf")
  
echo "Upload Response:"
echo "${UPLOAD_RESPONSE}" | jq '.'
RESUME_ID=$(echo "${UPLOAD_RESPONSE}" | jq -r '.id')
echo "Resume ID: ${RESUME_ID}"

# 2. Trigger synchronous parsing
echo -e "\n2. Triggering synchronous parsing..."
PARSE_RESPONSE=$(curl -s -X POST "${BASE_URL}/resume/parse/${RESUME_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"background": false, "use_llm": true, "generate_vectors": false}')
  
echo "Parse Response:"
echo "${PARSE_RESPONSE}" | jq '.'

# 3. Get parsed data
echo -e "\n3. Retrieving parsed data..."
GET_RESPONSE=$(curl -s -X GET "${BASE_URL}/resume/${RESUME_ID}" \
  -H "Authorization: Bearer ${TOKEN}")
  
echo "Resume Data:"
echo "${GET_RESPONSE}" | jq '.'

# 4. Trigger background parsing
echo -e "\n4. Triggering background parsing..."
BACKGROUND_RESPONSE=$(curl -s -X POST "${BASE_URL}/resume/parse/${RESUME_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"background": true, "use_llm": true, "generate_vectors": false}')
  
echo "Background Parse Response:"
echo "${BACKGROUND_RESPONSE}" | jq '.'

# 5. Get resume for review
echo -e "\n5. Getting resume for review..."
REVIEW_RESPONSE=$(curl -s -X GET "${BASE_URL}/resume/review/${RESUME_ID}" \
  -H "Authorization: Bearer ${TOKEN}")
  
echo "Review Data:"
echo "${REVIEW_RESPONSE}" | jq '.'

# 6. Apply manual corrections
echo -e "\n6. Applying manual corrections..."
VALIDATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/resume/validate/${RESUME_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "corrections": {
      "name": "John Smith",
      "summary": "Senior Software Engineer with 10+ years of experience"
    },
    "user_id": "'${RESUME_ID}'"
  }')
  
echo "Validation Response:"
echo "${VALIDATE_RESPONSE}" | jq '.'

echo -e "\n=== End of Examples ==="
# Resume Parsing Service

## Overview

The Resume Parsing Service is a production-ready microservice built with Python and FastAPI that extracts structured data from resumes in PDF, DOCX, and TXT formats. It leverages advanced NLP techniques, OCR fallback for scanned documents, LLM refinement, and optional vector embeddings for semantic search capabilities.

## Features

### Core Capabilities
- **Multi-format Support**: PDF (text-based and scanned with OCR), DOCX, TXT
- **Robust Text Extraction**: Uses pdfplumber, PyMuPDF, python-docx with OCR fallback via Tesseract
- **Modular NLP Pipeline**: Preprocessing, rule-based extraction, spaCy NER, skill taxonomy matching
- **LLM Refinement**: Normalizes dates, canonicalizes skills, generates summaries
- **Vector Embeddings**: Optional semantic embeddings for resume matching/search
- **Background Processing**: Supports both sync and async/background parsing
- **Manual Review Hooks**: APIs for human validation and corrections

### Security & Privacy
- **PII Protection**: Structured logging with sensitive data redaction
- **Signed URLs**: Secure file access with presigned URLs
- **GDPR Compliance**: Data retention policies and deletion capabilities

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   API Layer     │    │  Parsing Engine  │    │  Storage Layer   │
│                 │    │                  │    │                  │
│  POST /upload   │───▶│ Text Extraction  │───▶│  S3/MinIO        │
│  POST /parse    │    │ NLP Processing   │    │  PostgreSQL      │
│  GET /{id}      │    │ LLM Refinement   │    │                  │
│  POST /validate │    │ Vector Embedding │    │                  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## API Endpoints

### Upload Resume
```
POST /api/v1/resume/upload
Content-Type: multipart/form-data

file: resume.pdf
```

### Parse Resume
```
POST /api/v1/resume/parse/{resume_id}
Content-Type: application/json

{
  "background": false,
  "use_llm": true,
  "generate_vectors": false
}
```

### Get Parsed Data
```
GET /api/v1/resume/{resume_id}
```

### Manual Validation
```
POST /api/v1/resume/validate/{resume_id}
Content-Type: application/json

{
  "corrections": {
    "name": "John Smith",
    "emails": ["john.smith@example.com"]
  },
  "user_id": "uuid-of-editor"
}
```

### Review for Manual Edit
```
GET /api/v1/resume/review/{resume_id}
```

## Data Schema

The parsed resume data follows a comprehensive JSON schema with confidence scoring and provenance tracking:

```json
{
  "name": "string",
  "emails": ["string"],
  "phones": ["string"],
  "urls": ["string"],
  "linkedin": "string",
  "github": "string",
  "summary": "string",
  "skills": [
    {
      "skill": "string",
      "confidence": 0.95,
      "source": "exact_match"
    }
  ],
  "experiences": [
    {
      "company": "string",
      "title": "string",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "bullets": ["string"],
      "duration_months": 48,
      "confidence": 0.9
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "start_date": "2012-09-01",
      "end_date": "2016-05-01",
      "confidence": 0.85
    }
  ],
  "certifications": ["string"],
  "languages": ["string"],
  "locations": ["string"],
  "ocr_used": true,
  "parsing_confidence": 0.88,
  "generated_at": "2023-12-01T10:30:00Z",
  "provenance": {
    "contact_extraction": "regex",
    "entity_recognition": "spacy"
  }
}
```

## Integration with Qoder Agents

Agents can interact with the resume parsing service through these steps:

1. **Upload Resume**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/resume/upload" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@candidate_resume.pdf"
   ```

2. **Trigger Parsing**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/resume/parse/$RESUME_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"background": true}'
   ```

3. **Retrieve Results**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/resume/$RESUME_ID" \
        -H "Authorization: Bearer $TOKEN"
   ```

## Configuration

Environment variables for service configuration:

```bash
# Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=jobbuddy-resumes

# LLM (OpenAI)
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your-api-key

# Vector Service
VECTOR_PROVIDER=openai
VECTOR_MODEL=text-embedding-ada-002
VECTOR_API_KEY=your-api-key

# OCR
TESSERACT_PATH=/usr/bin/tesseract

# Rate Limiting
LLM_MIN_CALL_INTERVAL=1.0
```

## Performance Considerations

- **Batch Processing**: For bulk uploads, use background processing
- **Caching**: Cache frequent LLM normalizations to reduce costs
- **OCR Optimization**: Only perform OCR when no text is detected
- **GPU Acceleration**: For production, use GPU-enabled instances for transformer-based NER
- **Autoscaling**: Deploy workers with autoscaling based on queue depth

## Monitoring & Metrics

Key metrics to track:
- Parse success rate
- OCR usage rate
- Average parse time
- Fields confidence distribution
- LLM API costs

Prometheus metrics example:
```python
from prometheus_client import Counter, Histogram

PARSE_SUCCESS = Counter('resume_parse_success_total', 'Total successful parses')
PARSE_FAILURE = Counter('resume_parse_failures_total', 'Total parse failures')
PARSE_DURATION = Histogram('resume_parse_duration_seconds', 'Time spent parsing resumes')
```

## Error Handling & Fallbacks

The service gracefully handles:
- Corrupt or unsupported file formats
- OCR failures with retry mechanisms
- LLM timeouts with fallback to rule-based normalization
- Transient network issues with exponential backoff

Fallback strategies:
- If LLM unavailable: Use rule-based normalization
- If OCR fails: Mark low confidence and queue for manual review
- If NLP models fail: Fall back to regex-based extraction

## Deployment

### Docker Compose Example
```yaml
version: '3.8'
services:
  resume-parser:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - S3_ACCESS_KEY_ID=${S3_ACCESS_KEY_ID}
      - S3_SECRET_ACCESS_KEY=${S3_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
      - redis
  
  resume-worker:
    build: ./backend
    command: celery -A app.core.tasks worker --loglevel=info
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on:
      - redis
```

## Testing

Run tests with pytest:
```bash
pytest tests/test_resume.py -v
```

Tests cover:
- PDF text extraction (selectable + scanned via OCR mock)
- DOCX parsing
- Regex extraction for phone/email
- LLM adapter mocked test
- Endpoint tests using FastAPI TestClient

## Dependencies

Core requirements:
- FastAPI
- spaCy (en_core_web_sm or en_core_web_trf)
- pdfplumber, PyPDF2
- python-docx
- pytesseract (for OCR)
- openai (for LLM)
- sentence-transformers (for local embeddings)
- boto3 (for S3/MinIO)
- celery, redis (for background tasks)

Install with:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
"""
Prometheus metrics for the resume parsing service
"""

from prometheus_client import Counter, Histogram, Gauge

# Resume parsing metrics
PARSE_SUCCESS = Counter(
    'resume_parse_success_total',
    'Total number of successful resume parses',
    ['file_type']
)

PARSE_FAILURE = Counter(
    'resume_parse_failures_total',
    'Total number of failed resume parses',
    ['file_type', 'error_type']
)

PARSE_DURATION = Histogram(
    'resume_parse_duration_seconds',
    'Time spent parsing resumes',
    ['file_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

OCR_USAGE = Counter(
    'resume_ocr_usage_total',
    'Total number of resumes processed with OCR',
    ['file_type']
)

# LLM metrics
LLM_CALLS = Counter(
    'llm_calls_total',
    'Total number of LLM API calls',
    ['provider', 'model']
)

LLM_CALL_DURATION = Histogram(
    'llm_call_duration_seconds',
    'Time spent in LLM API calls',
    ['provider', 'model'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

LLM_COST = Counter(
    'llm_cost_total',
    'Total cost of LLM API calls',
    ['provider', 'model']
)

# Vector service metrics
VECTOR_EMBEDDINGS_GENERATED = Counter(
    'vector_embeddings_generated_total',
    'Total number of vector embeddings generated',
    ['provider', 'model']
)

VECTOR_EMBEDDING_DURATION = Histogram(
    'vector_embedding_duration_seconds',
    'Time spent generating vector embeddings',
    ['provider', 'model'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

# Confidence metrics
PARSING_CONFIDENCE = Histogram(
    'resume_parsing_confidence',
    'Distribution of parsing confidence scores',
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

SKILL_EXTRACTION_CONFIDENCE = Histogram(
    'skill_extraction_confidence',
    'Distribution of skill extraction confidence scores',
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

EXPERIENCE_EXTRACTION_CONFIDENCE = Histogram(
    'experience_extraction_confidence',
    'Distribution of experience extraction confidence scores',
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

# Queue metrics (for background processing)
BACKGROUND_QUEUE_SIZE = Gauge(
    'resume_background_queue_size',
    'Current size of the background parsing queue'
)

BACKGROUND_WORKER_COUNT = Gauge(
    'resume_background_worker_count',
    'Number of active background workers'
)
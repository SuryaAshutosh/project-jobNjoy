# Job Scraper Agent

A production-ready job scraping agent that discovers job postings from multiple sources, normalizes and deduplicates the data, and imports them into the JobBuddy backend.

## Features

- **Multi-source Support**: Scrapes jobs from LinkedIn, Adzuna, Monster, Naukri, Jooble, Greenhouse, Lever, Workable, and more
- **Modular Adapters**: Per-source adapters with API and scraping fallbacks
- **Data Normalization**: Standardizes job data from different sources
- **Deduplication**: Removes duplicate listings using exact and fuzzy matching
- **Proxy Support**: Rotates HTTP/HTTPS/SOCKS proxies to avoid rate limiting
- **CAPTCHA Handling**: Detects and handles CAPTCHA challenges
- **Scheduling**: Built-in scheduler for periodic scraping
- **Export Integration**: Pushes jobs to backend via POST /jobs/import

## Architecture

```
scraper_agent/
├── adapters/           # Per-source scraping adapters
│   ├── base.py         # Base adapter class
│   ├── linkedin.py     # LinkedIn scraping adapter
│   ├── adzuna.py       # Adzuna API adapter
│   ├── monster.py      # Monster scraping adapter
│   ├── naukri.py       # Naukri scraping adapter
│   ├── jooble.py       # Jooble API adapter
│   ├── greenhouse.py   # Greenhouse API adapter
│   ├── lever.py        # Lever API adapter
│   └── workable.py     # Workable API adapter
├── utils/              # Utility modules
│   ├── normalizer.py   # Data normalization
│   ├── deduplicator.py # Duplicate detection
│   ├── proxies.py      # Proxy management
│   └── scheduler.py    # Task scheduling
├── core.py             # Main agent logic
├── config.py           # Configuration
├── main.py             # Entry point
├── requirements.txt    # Dependencies
├── Dockerfile          # Containerization
└── tests/              # Unit tests
   └── test_scraper.py
```

## Supported Sources

1. **LinkedIn** - Web scraping with Playwright
2. **Adzuna** - Official API integration
3. **Monster** - Web scraping with Playwright
4. **Naukri** - Web scraping with Playwright (India-focused)
5. **Jooble** - Official API integration
6. **Greenhouse** - Official API integration for company career pages
7. **Lever** - Official API integration for company career pages
8. **Workable** - Official API integration for company career pages

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Configuration

Set environment variables:

```bash
export BACKEND_URL="http://your-backend-url:8000"
export SCRAPER_API_KEY="your-api-key"
export LOG_LEVEL="INFO"
```

Configure sources in [config.py](config.py):

```python
SOURCES_CONFIG = [
    {
        "name": "LinkedIn",
        "adapter": "linkedin",
        "adapter_class": "LinkedInAdapter",
        "params": {
            "page_limit": 3
        }
    },
    // ... more sources
]
```

## Usage

### Single Scraping Run

```bash
python main.py --mode single
```

### Scheduled Scraping

```bash
python main.py --mode schedule
```

### Docker Deployment

```bash
# Build image
docker build -t job-scraper-agent .

# Run container
docker run -e BACKEND_URL="http://your-backend:8000" -e SCRAPER_API_KEY="your-key" job-scraper-agent
```

## Integration with Backend

The agent exports jobs to the backend via `POST /api/jobs/import` with the following JSON structure:

```json
{
  "source_name": "linkedin",
  "source_id": "12345",
  "title": "React Developer",
  "company": "Acme Corp",
  "url": "https://...",
  "description": "Full job description html/text",
  "skills": ["React", "JavaScript"],
  "salary_min": 800000,
  "salary_max": 1200000,
  "location": "Bangalore, India",
  "posted_date": "2025-11-18T00:00:00Z",
  "raw_payload": { "...": "full raw data or html snippet" },
  "scraped_at": "2025-11-20T08:00:00Z",
  "confidence": 0.82
}
```

## Anti-Bot Measures

- **User-Agent Rotation**: Randomizes User-Agent headers
- **Request Delays**: Adds randomized delays between requests
- **Proxy Support**: Rotates through proxy pool
- **CAPTCHA Detection**: Detects and handles CAPTCHA challenges
- **Retry Logic**: Implements exponential backoff for transient errors

## Proxy Configuration

Configure proxies in [config.py](config.py):

```python
PROXY_CONFIG = {
    "proxies": [
        {
            "host": "proxy1.example.com",
            "port": 8080,
            "username": "user1",
            "password": "pass1",
            "protocol": "http"
        },
        {
            "host": "proxy2.example.com",
            "port": 1080,
            "protocol": "socks5"
        }
    ]
}
```

## CAPTCHA Handling

The agent includes CAPTCHA detection and handling:

1. **Detection**: Looks for CAPTCHA indicators in page content
2. **Bypass Attempt**: Switches proxy/User-Agent and retries once
3. **Manual Review**: Logs details for manual CAPTCHA solving

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

## Adding New Sources

1. Create a new adapter in [adapters/](adapters/)
2. Inherit from `BaseAdapter`
3. Implement `scrape_jobs()` method
4. Add to `SOURCES_CONFIG` in [config.py](config.py)

## Monitoring & Logging

The agent provides detailed logging for monitoring:

- Scraping progress per source
- Normalization and deduplication statistics
- Export success/failure rates
- Error details and stack traces

## Legal & Compliance

- Respects robots.txt by default
- Implements reasonable rate limiting
- Handles CAPTCHA challenges appropriately
- Complies with terms of service of job boards
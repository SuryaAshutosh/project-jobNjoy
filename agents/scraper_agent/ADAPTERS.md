# Job Scraper Adapters

This document describes the available job scraper adapters and how to configure them.

## Available Adapters

### 1. LinkedIn (`linkedin`)
Scrapes jobs from LinkedIn job search.

**Parameters:**
- `page_limit`: Number of pages to scrape (default: 3)

### 2. Adzuna (`adzuna`)
Uses the official Adzuna API for job listings.

**Parameters:**
- `max_pages`: Number of pages to fetch (default: 3)
- `per_page`: Number of jobs per page (default: 50)
- `salary_min`: Minimum salary filter
- `job_type`: Job type filter (e.g., 'fulltime')
- `remote`: Boolean to filter remote jobs

**Environment Variables:**
- `ADZUNA_APP_ID`: Your Adzuna app ID
- `ADZUNA_APP_KEY`: Your Adzuna app key

### 3. Monster (`monster`)
Scrapes jobs from Monster job board.

**Parameters:**
- `page_limit`: Number of pages to scrape (default: 3)

### 4. Naukri (`naukri`)
Scrapes jobs from Naukri job board (India).

**Parameters:**
- `page_limit`: Number of pages to scrape (default: 3)

### 5. Jooble (`jooble`)
Uses the official Jooble API for job listings.

**Parameters:**
- `max_pages`: Number of pages to fetch (default: 3)
- `salary_min`: Minimum salary filter
- `remote`: Boolean to filter remote jobs

**Environment Variables:**
- `JOOBLE_API_KEY`: Your Jooble API key

### 6. Greenhouse (`greenhouse`)
Uses the official Greenhouse API for company job boards.

**Parameters:**
- `board_token`: Board token (required)
- `content`: Include job content (true/false)

**Usage Example:**
```python
{
    "name": "Greenhouse",
    "adapter": "greenhouse",
    "adapter_class": "GreenhouseAdapter",
    "params": {
        "board_token": "company_board_token"
    }
}
```

### 7. Lever (`lever`)
Uses the official Lever API for company job boards.

**Parameters:**
- `clientname`: Client name (required)
- `mode`: Response mode ('json' or 'iframe')

**Usage Example:**
```python
{
    "name": "Lever",
    "adapter": "lever",
    "adapter_class": "LeverAdapter",
    "params": {
        "clientname": "company_name"
    }
}
```

### 8. Workable (`workable`)
Uses the official Workable API for company job boards.

**Parameters:**
- `clientname`: Client name (required)
- `limit`: Number of jobs to fetch

**Usage Example:**
```python
{
    "name": "Workable",
    "adapter": "workable",
    "adapter_class": "WorkableAdapter",
    "params": {
        "clientname": "company_name"
    }
}
```

### 9. Careerjet (`careerjet`)
Uses the official Careerjet API for job listings.

**Parameters:**
- `max_pages`: Number of pages to fetch (default: 3)
- `salary_min`: Minimum salary filter

**Environment Variables:**
- `CAREERJET_API_KEY`: Your Careerjet API key

**Usage Example:**
```python
{
    "name": "Careerjet",
    "adapter": "careerjet",
    "adapter_class": "CareerjetAdapter",
    "params": {
        "max_pages": 3
    }
}
```

## Adding New Adapters

To add a new adapter:

1. Create a new file in the `adapters/` directory
2. Inherit from `BaseAdapter`
3. Implement the `scrape_jobs` method
4. Add the adapter to `SOURCES_CONFIG` in `config.py`

Example:
```python
from adapters.base import BaseAdapter

class NewAdapter(BaseAdapter):
    async def scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implementation here
        pass
```
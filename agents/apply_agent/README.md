# Auto-Apply Agent

A production-grade automation agent that automatically applies to jobs on external job boards using browser automation, AI-based question answering, and integration with a FastAPI backend.

## Architecture Overview

The Auto-Apply Agent is designed with a modular, extensible architecture that supports multiple job sites through site-specific adapters. The agent follows a pipeline approach:

1. **Fetch** - Retrieve pending applications from the backend
2. **Navigate** - Open job application pages using headless browsers
3. **Detect** - Identify forms and question fields dynamically
4. **Fill** - Populate fields using parsed resume data
5. **Generate** - Create AI-powered answers for open-ended questions
6. **Upload** - Attach resume files
7. **Submit** - Complete the application process
8. **Report** - Callback the backend with results

## Key Components

### Core Components

- **[agent.py](agent.py)** - Main agent runner and workflow orchestrator
- **[workflow.py](workflow.py)** - Task orchestration and execution management
- **[form_detector.py](form_detector.py)** - Form field detection and analysis engine
- **[autofill_engine.py](autofill_engine.py)** - Intelligent form filling engine with fuzzy matching
- **[answer_generator.py](answer_generator.py)** - AI-driven answer generation using LLMs
- **[resume_uploader.py](resume_uploader.py)** - Resume file upload handling
- **[exporters/backend_client.py](exporters/backend_client.py)** - Secure backend API communication

### Site Adapters

- **[adapters/linkedin.py](adapters/linkedin.py)** - LinkedIn-specific application handling
- **[adapters/indeed.py](adapters/indeed.py)** - Indeed-specific application handling
- **[adapters/naukri.py](adapters/naukri.py)** - Naukri-specific application handling
- **[adapters/base.py](adapters/base.py)** - Abstract base class for all adapters

### Utilities

- **[utils/browser_pool.py](utils/browser_pool.py)** - Browser instance management with pooling
- **[utils/settings.py](utils/settings.py)** - Configuration management and loading
- **[utils/retry_handler.py](utils/retry_handler.py)** - Retry logic with exponential backoff

## Features

### Browser Automation
- Headless Chromium browser automation with Playwright
- Browser pooling for efficient resource usage
- Stealth mode to avoid bot detection
- Auto-wait for network idle and DOM stability
- Scrolling routines for long pages
- Comprehensive form field detection including React shadow DOM

### Intelligent Form Filling
- Fuzzy matching for field detection
- Confidence scoring for field mappings
- Support for name, email, phone, location, company, title, skills, and custom fields
- Configurable field mappings via [config.yaml](config.yaml)

### AI-Powered Answer Generation
- LLM integration (OpenAI) for generating tailored responses
- Prompt templates for common question types
- Fallback mechanisms when LLM fails
- Retry logic with exponential backoff
- PII sanitization in logs

### Error Handling & Reliability
- Maximum retries per job (configurable)
- CAPTCHA detection with manual review flagging
- Multi-step form handling (up to 3 steps)
- Graceful login wall handling
- Screenshot capture for debugging (base64 encoded)
- Comprehensive logging and metrics collection

### Security
- HMAC signing for secure backend communication
- Configurable proxy support
- Environment variable configuration for secrets

### Observability
- Structured JSON logging
- Metrics collection:
  - applications_attempted_total
  - applications_applied_total
  - applications_failed_total
  - captcha_detected_total
  - ai_answers_generated_total
- Optional Prometheus integration

## Configuration

The agent is configured through [config.yaml](config.yaml) with support for:

- Backend settings (URL, secret key)
- Browser settings (headless, slow motion, timeouts)
- Proxy settings (enabled/disabled, URLs, credentials)
- LLM settings (provider, model, API key, parameters)
- Site-specific overrides
- Field mappings
- Logging settings
- Retry settings
- CAPTCHA detection keywords

## Deployment

### Docker

```bash
# Build the image
docker build -t auto-apply-agent .

# Run the agent
docker run auto-apply-agent
```

### Docker Compose

```bash
# Start the service
docker-compose up -d
```

### Kubernetes

Deploy using the provided [k8s-cronjob.yaml](k8s-cronjob.yaml) which runs the agent every 30 minutes.

### Direct Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run single cycle
python main.py --mode single

# Run continuously
python main.py --mode continuous --interval 1800
```

## Testing

The agent includes a comprehensive test suite using pytest:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_backend_client.py
```

Test coverage includes:
- Form detection
- Autofill mapping
- AI answer generation (with mock LLM)
- Backend communication
- Resume uploading
- Retry handling

## Health Check

Verify agent components with the health check script:

```bash
python health_check.py
```

## Setup

Platform-specific setup scripts are provided:
- [setup.sh](setup.sh) for Unix-like systems
- [setup.bat](setup.bat) for Windows

These scripts:
1. Create a virtual environment
2. Install dependencies
3. Install Playwright browsers
4. Create necessary directories
5. Run health check

## Integration with Backend

The agent integrates with the JobBuddy backend through:

1. **Fetching Applications**: `GET /api/applications?status=pending_auto_apply`
2. **Getting Job Details**: `GET /api/jobs/{job_id}`
3. **Getting Resume Data**: `GET /api/resume/{resume_id}`
4. **Submitting Results**: `POST /api/agents/submit-application-result`

All communication is secured with HMAC signatures.

## Extending to New Job Sites

To add support for a new job site:

1. Create a new adapter in the [adapters/](adapters/) directory
2. Extend the [BaseAdapter](adapters/base.py) class
3. Implement required methods:
   - `detect_login_page()`
   - `handle_login()`
   - `detect_application_form()`
   - `handle_multi_step_application()`
4. Add site configuration to [config.yaml](config.yaml)
5. Register the adapter in [agent.py](agent.py)

## Sample Output

See [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md) for example console output, log entries, and API payloads.

## Requirements

- Python 3.8+
- Playwright-compatible browser (Chromium)
- OpenAI API key (for AI features)
- Access to JobBuddy backend

## Dependencies

See [requirements.txt](requirements.txt) for the complete list of Python dependencies.
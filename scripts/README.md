# JobBuddy Smoke Testing System

This directory contains automated smoke tests for the JobBuddy platform to ensure all components work correctly before deployment.

## Components

1. **Bash Smoke Test** (`full_smoke_test.sh`) - Comprehensive shell script testing
2. **Python Smoke Runner** (`smoke_runner.py`) - Programmatic test runner with detailed reporting
3. **Qoder Agent** (`qoder_agent.py`) - Automated agent with retry logic and fix recommendations
4. **Sample Fixtures** - Test data files in the `fixtures/` directory

## Running the Tests

### Option 1: Bash Smoke Test
```bash
bash scripts/full_smoke_test.sh
```

This script will:
- Start docker-compose services
- Wait for services to be healthy
- Run database migrations
- Execute backend and frontend tests
- Perform API tests via curl
- Generate logs in `logs/smoke/`
- Exit with appropriate status code

### Option 2: Python Smoke Runner
```bash
python3 scripts/smoke_runner.py
```

Additional options:
```bash
# Skip certain test categories
python3 scripts/smoke_runner.py --skip-resume --skip-stripe --skip-agents

# Custom base URL
python3 scripts/smoke_runner.py --base-url http://your-api-url:8000

# Custom output file
python3 scripts/smoke_runner.py --output-file custom_report.json
```

### Option 3: Qoder Agent (Recommended)
```bash
python3 scripts/qoder_agent.py
```

Additional options:
```bash
# Set retry count
python3 scripts/qoder_agent.py --max-retries 5

# Skip certain test categories
python3 scripts/qoder_agent.py --skip-resume --skip-stripe --skip-agents
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Smoke Test
on: [push, pull_request]
jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: 18
    - name: Set up Docker
      uses: docker/setup-buildx-action@v1
    - name: Run Smoke Test
      run: |
        python3 scripts/qoder_agent.py
```

### GitLab CI Example
```yaml
smoke_test:
  stage: test
  script:
    - python3 scripts/qoder_agent.py
  artifacts:
    reports:
      junit: reports/smoke_report.json
```

## Reading Results

### Log Files
- `logs/smoke/full_smoke_test.log` - Bash script logs
- `logs/smoke/backend.log` - Backend service logs
- `logs/smoke/frontend.log` - Frontend test logs

### Report Files
- `reports/smoke_report.json` - Detailed JSON report from Python runner
- `reports/smoke_summary.txt` - Human-readable summary from Qoder Agent

### Exit Codes
- `0` - All tests passed, ready for deployment
- `1` - Some tests failed, fix required

## Test Coverage

The smoke tests verify the following components:

1. **Platform Health**
   - Service availability
   - Database connectivity
   - API responsiveness

2. **Authentication**
   - User registration
   - User login
   - Profile retrieval

3. **Resume Management**
   - Resume upload
   - Resume parsing

4. **Job Management**
   - Job import
   - Job listing

5. **Application Processing**
   - Application creation
   - Agent callback handling

6. **Payment Integration**
   - Stripe webhook processing

## Troubleshooting

If tests fail:

1. Check `logs/smoke/` directory for detailed error logs
2. Verify docker-compose services are running: `docker-compose -f infra/docker-compose.yml ps`
3. Check service logs: `docker-compose -f infra/docker-compose.yml logs [service]`
4. Ensure all environment variables are set correctly
5. Review the recommendations in `reports/smoke_summary.txt`

## Customization

To customize the tests:

1. Modify fixture files in `fixtures/` directory
2. Adjust test parameters in the scripts
3. Add new test cases to `smoke_runner.py`
4. Update API endpoints if they change
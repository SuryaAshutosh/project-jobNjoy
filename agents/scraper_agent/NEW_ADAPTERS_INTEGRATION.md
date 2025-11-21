# Integration of New Job API Adapters

This document explains how to integrate and use the new job API adapters that have been added to the scraper agent.

## Overview

Five new adapters have been added to support popular job APIs:
1. Jooble API
2. Greenhouse API
3. Lever API
4. Workable API
5. Careerjet API

These adapters follow the same pattern as existing adapters and can be easily configured in the scraper agent.

## Prerequisites

Before using these adapters, ensure you have:
1. API keys for the services that require them (Jooble, Careerjet)
2. Board tokens for Greenhouse
3. Client names for Lever and Workable

## Configuration

The new adapters are already added to the [config.py](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/config.py) file in the `SOURCES_CONFIG` list. You can enable them by uncommenting or modifying the entries.

### Jooble Adapter

To use the Jooble adapter, you need to set your API key:

```bash
export JOOBLE_API_KEY=your_actual_api_key_here
```

Configuration example:
```python
{
    "name": "Jooble",
    "adapter": "jooble",
    "adapter_class": "JoobleAdapter",
    "params": {
        "max_pages": 3
    }
}
```

### Greenhouse Adapter

To use the Greenhouse adapter, you need a board token:

Configuration example:
```python
{
    "name": "Greenhouse",
    "adapter": "greenhouse",
    "adapter_class": "GreenhouseAdapter",
    "params": {
        "board_token": "your_board_token_here"
    }
}
```

### Lever Adapter

To use the Lever adapter, you need a client name:

Configuration example:
```python
{
    "name": "Lever",
    "adapter": "lever",
    "adapter_class": "LeverAdapter",
    "params": {
        "clientname": "your_client_name_here"
    }
}
```

### Workable Adapter

To use the Workable adapter, you need a client name:

Configuration example:
```python
{
    "name": "Workable",
    "adapter": "workable",
    "adapter_class": "WorkableAdapter",
    "params": {
        "clientname": "your_client_name_here"
    }
}
```

### Careerjet Adapter

To use the Careerjet adapter, you need to set your API key:

```bash
export CAREERJET_API_KEY=your_actual_api_key_here
```

Configuration example:
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

## Running the Scraper

To run the scraper with the new adapters:

1. Make sure your environment variables are set
2. Update the configuration in [config.py](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/config.py) as needed
3. Run the scraper agent:

```bash
cd agents/scraper_agent
python main.py
```

## Testing the Adapters

Unit tests for the new adapters are located in [tests/test_new_adapters.py](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/tests/test_new_adapters.py). You can run them with:

```bash
cd agents/scraper_agent
python -m pytest tests/test_new_adapters.py
```

## Usage Examples

See [examples/new_adapters_example.py](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/examples/new_adapters_example.py) for detailed usage examples of each adapter.

## Adding More Adapters

To add more adapters from the list of job APIs:

1. Create a new adapter file in the `adapters/` directory
2. Inherit from `BaseAdapter`
3. Implement the `scrape_jobs` method
4. Add the adapter to `SOURCES_CONFIG` in [config.py](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/config.py)
5. Add tests in the `tests/` directory
6. Add documentation to [ADAPTERS.md](file:///c:/Users/Surya/Desktop/New folder/project-jobNjoy/agents/scraper_agent/ADAPTERS.md)

## Supported Job APIs

The following job APIs from your list are now supported:

1. **Jooble API** - General job search engine
2. **Greenhouse API** - For company career pages using Greenhouse
3. **Lever API** - For company career pages using Lever
4. **Workable API** - For company career pages using Workable
5. **Careerjet API** - International job search engine

Additional APIs can be implemented following the same pattern.

## Troubleshooting

If you encounter issues:

1. Check that API keys and tokens are correctly set
2. Verify that the API endpoints are accessible
3. Check the logs for error messages
4. Ensure you're not exceeding rate limits
5. Verify that the parameters in the configuration are correct

## Next Steps

Consider implementing adapters for:
- Indeed Job Sync API
- Google Cloud Talent Solution
- Other APIs from your list

The existing adapters provide a solid foundation for implementing these additional APIs.
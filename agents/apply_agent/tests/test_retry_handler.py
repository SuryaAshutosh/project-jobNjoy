"""
Unit tests for RetryHandler
"""

import pytest
from unittest.mock import Mock, AsyncMock
from ..utils.retry_handler import retry_with_backoff, RetryHandler

def test_retry_with_backoff_success():
    """Test retry decorator with successful function"""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3)
    def test_function():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = test_function()
    assert result == "success"
    assert call_count == 1

def test_retry_with_backoff_failure():
    """Test retry decorator with failing function"""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3)
    def test_function():
        nonlocal call_count
        call_count += 1
        raise Exception("Test error")
    
    with pytest.raises(Exception, match="Test error"):
        test_function()
    
    assert call_count == 3

def test_retry_with_backoff_eventual_success():
    """Test retry decorator with eventual success"""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3)
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Test error")
        return "success"
    
    result = test_function()
    assert result == "success"
    assert call_count == 2

@pytest.mark.asyncio
async def test_retry_handler_async():
    """Test RetryHandler with async function"""
    call_count = 0
    
    async def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Test error")
        return "success"
    
    retry_handler = RetryHandler(max_attempts=3)
    result = await retry_handler.execute_with_retry(test_function)
    
    assert result == "success"
    assert call_count == 2

@pytest.mark.asyncio
async def test_retry_handler_async_failure():
    """Test RetryHandler with failing async function"""
    call_count = 0
    
    async def test_function():
        nonlocal call_count
        call_count += 1
        raise Exception("Test error")
    
    retry_handler = RetryHandler(max_attempts=3)
    
    with pytest.raises(Exception, match="Test error"):
        await retry_handler.execute_with_retry(test_function)
    
    assert call_count == 3
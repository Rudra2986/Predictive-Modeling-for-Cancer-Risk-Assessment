import os
import sys
import time
import pytest
from fastapi import HTTPException

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.services.rate_limiter_service import RateLimiterService

def test_rate_limiter_allows_requests():
    """
    Verify rate limiter allows requests within limits.
    """
    limiter = RateLimiterService(limit=5, window_seconds=60)
    
    # Send 5 requests for user 1 - all should succeed without raising exception
    for _ in range(5):
        limiter.check_rate_limit(user_id=1)

def test_rate_limiter_blocks_requests_exceeding_limit():
    """
    Verify rate limiter raises 429 error once limits are exceeded.
    """
    limiter = RateLimiterService(limit=2, window_seconds=60)
    
    # 1st request
    limiter.check_rate_limit(user_id=2)
    # 2nd request
    limiter.check_rate_limit(user_id=2)
    
    # 3rd request should raise HTTPException with 429 status code
    with pytest.raises(HTTPException) as exc_info:
        limiter.check_rate_limit(user_id=2)
    
    assert exc_info.value.status_code == 429
    assert "Too many requests" in exc_info.value.detail

def test_rate_limiter_sliding_window_expiration():
    """
    Verify that requests are allowed again after the sliding window expires.
    """
    limiter = RateLimiterService(limit=1, window_seconds=1)
    
    # 1st request
    limiter.check_rate_limit(user_id=3)
    
    # Exceeds immediately
    with pytest.raises(HTTPException) as exc_info:
        limiter.check_rate_limit(user_id=3)
    assert exc_info.value.status_code == 429
    
    # Wait for the window to expire
    time.sleep(1.1)
    
    # Request should now succeed
    limiter.check_rate_limit(user_id=3)

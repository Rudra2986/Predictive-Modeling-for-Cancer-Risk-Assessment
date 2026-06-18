import time
from typing import Dict, List
from fastapi import HTTPException, status

class RateLimiterService:
    def __init__(self, limit: int = 20, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        # In-memory store: user_id -> list of request timestamps
        self._requests: Dict[int, List[float]] = {}

    def check_rate_limit(self, user_id: int) -> None:
        """
        Validates if the user has exceeded their request quota.
        Raises HTTPException 429 if the limit is exceeded.
        """
        now = time.time()
        
        if user_id not in self._requests:
            self._requests[user_id] = [now]
            return
            
        # Filter out timestamps older than the sliding window
        cutoff = now - self.window_seconds
        self._requests[user_id] = [t for t in self._requests[user_id] if t > cutoff]
        
        # Check quota limit
        if len(self._requests[user_id]) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please wait a minute before sending another message."
            )
            
        # Record this successful request
        self._requests[user_id].append(now)

# Instantiate global service instance
rate_limiter = RateLimiterService()

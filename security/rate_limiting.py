import redis
import os
from datetime import timedelta
from loguru import logger
from telegram import Update

# Initialize Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def rate_limit_user(user_id: int, command: str) -> bool:
    """Enforce rate limits using Redis"""
    key = f"rate_limit:{user_id}:{command}"
    current_count = redis_client.get(key)
    
    # Get rate limits from environment
    limits = {
        "generate": os.getenv("RATE_LIMIT_GENERATE", "5/30"),  # 5 requests per 30 seconds
        "history": os.getenv("RATE_LIMIT_HISTORY", "10/60"),
        "stats": os.getenv("RATE_LIMIT_STATS", "10/60")
    }
    
    if command not in limits:
        return False
    
    max_requests, period_seconds = map(int, limits[command].split('/'))
    
    if current_count is None:
        redis_client.setex(key, period_seconds, 1)
        return False
    
    if int(current_count) >= max_requests:
        return True
    
    redis_client.incr(key)
    return False

def clear_rate_limits(user_id: int):
    """Clear all rate limits for a user (admin function)"""
    keys = redis_client.keys(f"rate_limit:{user_id}:*")
    if keys:
        redis_client.delete(*keys)
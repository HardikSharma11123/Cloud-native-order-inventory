import redis
from app.core.config import settings
from typing import Optional


redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # Automatically decode bytes to strings
    max_connections=10
)

def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)



def test_redis_connection() -> bool:
    """Test if Redis connection is working"""
    try:
        client = get_redis()
        client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
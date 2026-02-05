"""
Redis connection and caching
"""
import json
from typing import Any, Optional
import redis.asyncio as redis

from app.core.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=20
)

# Global Redis client for use throughout the app
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(connection_pool=redis_pool)
    return redis_client


async def close_redis() -> None:
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class Cache:
    """Cache utilities"""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        r = await get_redis()
        value = await r.get(key)
        if value:
            return json.loads(value)
        return None
    
    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600) -> None:
        """Set value in cache with expiration (default 1 hour)"""
        r = await get_redis()
        await r.set(key, json.dumps(value), ex=expire)
    
    @staticmethod
    async def delete(key: str) -> None:
        """Delete value from cache"""
        r = await get_redis()
        await r.delete(key)
    
    @staticmethod
    async def delete_pattern(pattern: str) -> None:
        """Delete all keys matching pattern"""
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
    
    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """Increment a counter"""
        r = await get_redis()
        return await r.incrby(key, amount)
    
    @staticmethod
    async def expire(key: str, seconds: int) -> None:
        """Set expiration on a key"""
        r = await get_redis()
        await r.expire(key, seconds)


class RateLimiter:
    """Rate limiting using Redis"""
    
    @staticmethod
    async def is_allowed(key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed under rate limit"""
        r = await get_redis()
        
        current = await r.get(key)
        if current is None:
            await r.set(key, 1, ex=window_seconds)
            return True
        
        if int(current) >= max_requests:
            return False
        
        await r.incr(key)
        return True
    
    @staticmethod
    async def get_remaining(key: str, max_requests: int) -> int:
        """Get remaining requests in window"""
        r = await get_redis()
        current = await r.get(key)
        if current is None:
            return max_requests
        return max(0, max_requests - int(current))

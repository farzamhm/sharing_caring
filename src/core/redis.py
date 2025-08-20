"""Redis configuration and connection management."""

from typing import AsyncGenerator, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool: Optional[Redis] = None


async def init_redis() -> Redis:
    """Initialize Redis connection pool."""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return redis_pool


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency to get Redis connection."""
    redis_client = await init_redis()
    try:
        yield redis_client
    finally:
        # Connection is returned to pool automatically
        pass


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None


class RedisService:
    """Service for common Redis operations."""
    
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client
    
    async def set_with_ttl(self, key: str, value: str, ttl_seconds: int) -> None:
        """Set key with TTL."""
        await self.redis.setex(key, ttl_seconds, value)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return await self.redis.get(key)
    
    async def delete(self, key: str) -> None:
        """Delete key."""
        await self.redis.delete(key)
    
    async def increment(self, key: str) -> int:
        """Increment counter."""
        return await self.redis.incr(key)
    
    async def set_user_state(
        self, 
        user_id: int, 
        state: str, 
        data: Optional[str] = None,
        ttl: int = 3600
    ) -> None:
        """Set user conversation state."""
        state_key = f"user_state:{user_id}"
        await self.redis.hset(state_key, mapping={
            "state": state,
            "data": data or "",
        })
        await self.redis.expire(state_key, ttl)
    
    async def get_user_state(self, user_id: int) -> Optional[dict]:
        """Get user conversation state."""
        state_key = f"user_state:{user_id}"
        state_data = await self.redis.hgetall(state_key)
        if not state_data:
            return None
        return {
            "state": state_data.get("state"),
            "data": state_data.get("data"),
        }
    
    async def clear_user_state(self, user_id: int) -> None:
        """Clear user conversation state."""
        state_key = f"user_state:{user_id}"
        await self.redis.delete(state_key)
    
    async def rate_limit_check(self, identifier: str, limit: int, window: int) -> bool:
        """Check rate limit for identifier."""
        key = f"rate_limit:{identifier}"
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, window, "1")
            return True
        
        if int(current) >= limit:
            return False
        
        await self.redis.incr(key)
        return True
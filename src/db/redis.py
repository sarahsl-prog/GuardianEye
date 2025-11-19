"""Redis client for caching and session management."""

from typing import Optional
import redis.asyncio as redis

from src.config.settings import settings


_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance.

    Returns:
        Redis client
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    return _redis_client


async def close_redis_client():
    """Close Redis client connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None

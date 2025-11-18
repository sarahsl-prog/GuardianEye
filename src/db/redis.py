"""Redis connection and utilities."""

import redis.asyncio as redis

from src.config.settings import settings


async def get_redis_client():
    """
    Create Redis client.

    Returns:
        Redis client instance
    """
    client = await redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    return client


async def close_redis_client(client):
    """
    Close Redis client.

    Args:
        client: Redis client to close
    """
    await client.close()

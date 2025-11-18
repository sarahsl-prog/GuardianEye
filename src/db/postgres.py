"""PostgreSQL database connection and utilities."""

import asyncpg

from src.config.settings import settings


async def get_postgres_pool():
    """
    Create PostgreSQL connection pool.

    Returns:
        asyncpg connection pool
    """
    pool = await asyncpg.create_pool(
        settings.postgres_url,
        min_size=1,
        max_size=10,
    )
    return pool


async def close_postgres_pool(pool):
    """
    Close PostgreSQL connection pool.

    Args:
        pool: Connection pool to close
    """
    await pool.close()

"""PostgreSQL connection for state persistence."""

from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.config.settings import settings


_engine: Optional[AsyncEngine] = None


def get_postgres_connection() -> AsyncEngine:
    """Get PostgreSQL async engine.

    Returns:
        SQLAlchemy async engine
    """
    global _engine

    if _engine is None:
        _engine = create_async_engine(
            settings.postgres_url,
            echo=settings.app_env == "development",
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

    return _engine


async def close_postgres_connection():
    """Close PostgreSQL connection."""
    global _engine

    if _engine:
        await _engine.dispose()
        _engine = None

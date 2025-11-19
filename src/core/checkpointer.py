"""Checkpointer configuration for state persistence."""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.config.settings import settings


async def get_checkpointer() -> AsyncPostgresSaver | AsyncSqliteSaver:
    """Get appropriate checkpointer based on environment.

    Returns:
        Checkpointer instance (PostgreSQL for production, SQLite for dev)
    """
    if settings.app_env == "production":
        # PostgreSQL for production
        checkpointer = AsyncPostgresSaver.from_conn_string(
            settings.postgres_url.replace("postgresql+asyncpg://", "postgresql://")
        )
        await checkpointer.setup()
        return checkpointer
    else:
        # SQLite for development
        checkpointer = AsyncSqliteSaver.from_conn_string("checkpoints.db")
        await checkpointer.setup()
        return checkpointer

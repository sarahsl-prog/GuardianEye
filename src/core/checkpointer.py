"""State persistence setup using LangGraph checkpointers."""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.config.settings import settings


async def get_checkpointer():
    """
    Get appropriate checkpointer based on environment.

    Returns:
        AsyncPostgresSaver for production, AsyncSqliteSaver for development
    """
    if settings.is_production:
        # PostgreSQL for production
        checkpointer = AsyncPostgresSaver.from_conn_string(
            settings.postgres_url
        )
        await checkpointer.setup()
        return checkpointer
    else:
        # SQLite for development
        checkpointer = AsyncSqliteSaver.from_conn_string(
            "checkpoints.db"
        )
        await checkpointer.setup()
        return checkpointer

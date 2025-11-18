"""Database initialization script."""

import asyncio

from src.core.checkpointer import get_checkpointer


async def setup_database():
    """Initialize database tables and checkpointer."""
    print("Setting up database...")

    # Initialize checkpointer (creates tables)
    checkpointer = await get_checkpointer()
    print("✓ Checkpointer initialized")

    # TODO: Add additional database setup as needed
    # - Create user tables
    # - Create session tables
    # - Initialize vector store

    print("✓ Database setup complete!")


if __name__ == "__main__":
    asyncio.run(setup_database())

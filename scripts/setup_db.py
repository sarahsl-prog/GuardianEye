"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

from src.core.checkpointer import get_checkpointer
from src.db.postgres import get_postgres_connection
from src.db.redis import get_redis_client
from src.db.vector_store import initialize_vector_store, seed_security_knowledge
from src.config.settings import settings


async def setup_database():
    """Initialize database tables and checkpointer."""
    print("=" * 60)
    print("GuardianEye Database Setup")
    print("=" * 60)
    print(f"Environment: {settings.app_env}")
    print()

    # 1. Initialize checkpointer (creates LangGraph state tables)
    print("[1/5] Initializing checkpointer...")
    try:
        checkpointer = await get_checkpointer()
        print("✓ Checkpointer initialized (LangGraph state tables created)")
    except Exception as e:
        print(f"✗ Failed to initialize checkpointer: {e}")
        sys.exit(1)

    # 2. Test PostgreSQL connection
    print("\n[2/5] Testing PostgreSQL connection...")
    try:
        engine = get_postgres_connection()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✓ PostgreSQL connected: {version.split(',')[0]}")
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("  Please ensure PostgreSQL is running and connection string is correct.")
        sys.exit(1)

    # 3. Test Redis connection
    print("\n[3/5] Testing Redis connection...")
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        info = await redis_client.info("server")
        redis_version = info.get("redis_version", "unknown")
        print(f"✓ Redis connected: v{redis_version}")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("  Please ensure Redis is running and connection string is correct.")
        sys.exit(1)

    # 4. Initialize vector store
    print("\n[4/5] Initializing vector store (Chroma)...")
    try:
        vector_store = initialize_vector_store()

        # Create persistence directory
        persist_dir = Path(settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ Vector store initialized at: {persist_dir.absolute()}")
        print(f"  Collection: guardianeye_knowledge")

        # Seed with security knowledge
        print("  Seeding security knowledge base...")
        seed_security_knowledge()
        print("  ✓ Security knowledge documents added")

    except Exception as e:
        print(f"✗ Vector store initialization failed: {e}")
        print("  Note: This requires OpenAI API key for embeddings.")
        print("  You can skip this by not using RAG features.")

    # 5. Create additional tables (if models are implemented)
    print("\n[5/5] Checking for additional tables...")
    try:
        # This section can be expanded when models.py is implemented
        # For now, just verify the connection
        async with engine.connect() as conn:
            # Check if we need to create any custom tables
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public';"
                )
            )
            tables = [row[0] for row in result]

            if tables:
                print(f"✓ Found {len(tables)} existing tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("  No custom tables found (using LangGraph state tables only)")

    except Exception as e:
        print(f"  Note: Could not check tables: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Database Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run 'python scripts/seed_data.py' to add sample data (optional)")
    print("2. Start the application with 'python -m src.main' or 'uvicorn src.main:app'")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print()


async def teardown_database():
    """Clean up database (useful for testing)."""
    print("=" * 60)
    print("GuardianEye Database Teardown")
    print("=" * 60)

    # Close connections
    print("Closing connections...")

    from src.db.postgres import close_postgres_connection
    from src.db.redis import close_redis_client

    await close_postgres_connection()
    print("✓ PostgreSQL connection closed")

    await close_redis_client()
    print("✓ Redis connection closed")

    print("\n✓ Teardown complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--teardown":
        asyncio.run(teardown_database())
    else:
        asyncio.run(setup_database())

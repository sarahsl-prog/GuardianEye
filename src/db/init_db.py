"""Database initialization module."""

import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.postgres import get_postgres_connection
from src.db.models import Base, create_tables, User, UserRole
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def initialize_database():
    """Initialize the database with tables and indexes."""
    print("\n" + "=" * 60)
    print("Initializing Database Tables")
    print("=" * 60)

    engine = get_postgres_connection()

    try:
        # Create all tables
        print("\n[1/3] Creating database tables...")
        await create_tables(engine)
        print("✓ Tables created successfully")

        # Verify tables were created
        print("\n[2/3] Verifying tables...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name;"
                )
            )
            tables = [row[0] for row in result]

            if tables:
                print(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("⚠ No tables found")

        # Verify indexes
        print("\n[3/3] Verifying indexes...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE schemaname = 'public' ORDER BY indexname;"
                )
            )
            indexes = [row[0] for row in result]
            print(f"✓ Created {len(indexes)} indexes")

        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_database_connection():
    """Verify database connection and basic operations."""
    print("\nVerifying database connection...")

    engine = get_postgres_connection()

    try:
        async with engine.connect() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✓ PostgreSQL connected: {version.split(',')[0]}")

            # Check if tables exist
            result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public';"
                )
            )
            table_count = result.scalar()
            print(f"✓ Found {table_count} tables in database")

            return True

    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


async def create_admin_user_if_not_exists():
    """Create a default admin user if no users exist."""
    engine = get_postgres_connection()
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        # Check if any users exist
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            print("\nNo users found. Creating default admin user...")

            admin_user = User(
                username="admin",
                email="admin@guardianeye.local",
                hashed_password=pwd_context.hash("admin"),
                role=UserRole.ADMIN,
                full_name="System Administrator",
                is_active=True
            )

            session.add(admin_user)
            await session.commit()

            print("✓ Created default admin user:")
            print("  Username: admin")
            print("  Password: admin")
            print("  ⚠ CHANGE THIS PASSWORD IN PRODUCTION!")

            return True
        else:
            print(f"\n✓ Database already has {len(users)} user(s)")
            return False


if __name__ == "__main__":
    async def main():
        # Initialize database
        success = await initialize_database()

        if success:
            # Verify connection
            await verify_database_connection()

            # Create admin user if needed
            await create_admin_user_if_not_exists()

    asyncio.run(main())

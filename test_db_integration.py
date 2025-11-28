#!/usr/bin/env python
"""Quick test script for database integration."""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.db.postgres import get_postgres_connection
from src.db.models import create_tables, drop_tables, User, Session, AuditLog, UserRole, AuditAction
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def test_database_integration():
    """Test database models and operations."""
    print("\n" + "=" * 70)
    print(" " * 20 + "Database Integration Test")
    print("=" * 70)

    engine = get_postgres_connection()

    try:
        # Step 1: Create tables
        print("\n[1/7] Creating database tables...")
        await create_tables(engine)
        print("✓ Tables created")

        # Step 2: Create async session
        print("\n[2/7] Creating database session...")
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        print("✓ Session factory created")

        async with AsyncSessionLocal() as session:
            # Step 3: Create a test user
            print("\n[3/7] Creating test user...")
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=pwd_context.hash("testpass123"),
                role=UserRole.ANALYST,
                full_name="Test User",
                is_active=True
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"✓ Created user: {test_user.username} (ID: {test_user.id})")

            # Step 4: Create a session for the user
            print("\n[4/7] Creating user session...")
            user_session = Session(
                user_id=test_user.id,
                title="Test Session",
                thread_id="test-thread-123",
                context={"test": "data"},
                is_active=True
            )
            session.add(user_session)
            await session.commit()
            await session.refresh(user_session)
            print(f"✓ Created session: {user_session.id}")

            # Step 5: Create an audit log
            print("\n[5/7] Creating audit log...")
            audit = AuditLog(
                user_id=test_user.id,
                action=AuditAction.LOGIN,
                details={"ip": "127.0.0.1"},
                description="Test login",
                ip_address="127.0.0.1",
                success=True
            )
            session.add(audit)
            await session.commit()
            await session.refresh(audit)
            print(f"✓ Created audit log: {audit.id}")

            # Step 6: Query and verify relationships
            print("\n[6/7] Testing relationships...")

            # Load user with relationships
            result = await session.execute(
                select(User).where(User.username == "testuser")
            )
            loaded_user = result.scalar_one()

            print(f"✓ User: {loaded_user.username}")
            print(f"  - Sessions: {len(loaded_user.sessions)}")
            print(f"  - Audit logs: {len(loaded_user.audit_logs)}")

            assert len(loaded_user.sessions) == 1, "Should have 1 session"
            assert len(loaded_user.audit_logs) == 1, "Should have 1 audit log"

            # Step 7: Test cascading delete
            print("\n[7/7] Testing cascade delete...")
            await session.delete(loaded_user)
            await session.commit()
            print("✓ User deleted (sessions and audit logs should cascade)")

            # Verify cascade worked
            session_result = await session.execute(
                select(Session).where(Session.id == user_session.id)
            )
            deleted_session = session_result.scalar_one_or_none()
            assert deleted_session is None, "Session should be deleted"
            print("✓ Cascade delete verified")

        # Summary
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nDatabase integration is working correctly:")
        print("  ✓ Tables created")
        print("  ✓ User model working")
        print("  ✓ Session model working")
        print("  ✓ Audit log model working")
        print("  ✓ Relationships working")
        print("  ✓ Cascade deletes working")
        print()

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print("\n[Cleanup] Dropping test tables...")
        try:
            await drop_tables(engine)
            print("✓ Tables dropped")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")

        await engine.dispose()


if __name__ == "__main__":
    result = asyncio.run(test_database_integration())
    sys.exit(0 if result else 1)

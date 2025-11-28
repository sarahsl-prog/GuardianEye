# GuardianEye Testing Guide

**Status:** Database Integration Complete - Ready for Testing
**Date:** 2024-11-27

---

## 🚀 Quick Start - Test Database Integration

### Step 1: Start PostgreSQL

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for it to be ready (watch logs)
docker-compose logs -f postgres
# Press Ctrl+C when you see: "database system is ready to accept connections"
```

### Step 2: Run Integration Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run the comprehensive database test
PYTHONPATH=$(pwd) python test_db_integration.py
```

**Expected Output:**
```
======================================================================
                    Database Integration Test
======================================================================

[1/7] Creating database tables...
✓ Tables created

[2/7] Creating database session...
✓ Session factory created

[3/7] Creating test user...
✓ Created user: testuser (ID: ...)

[4/7] Creating user session...
✓ Created session: ...

[5/7] Creating audit log...
✓ Created audit log: ...

[6/7] Testing relationships...
✓ User: testuser
  - Sessions: 1
  - Audit logs: 1

[7/7] Testing cascade delete...
✓ User deleted (sessions and audit logs should cascade)
✓ Cascade delete verified

======================================================================
✅ ALL TESTS PASSED!
======================================================================

Database integration is working correctly:
  ✓ Tables created
  ✓ User model working
  ✓ Session model working
  ✓ Audit log model working
  ✓ Relationships working
  ✓ Cascade deletes working
```

✅ **If you see this output, Phase 1 is complete and working!**

### Step 3: Initialize Production Database

```bash
# Create tables and default admin user
PYTHONPATH=$(pwd) python src/db/init_db.py
```

**Expected Output:**
```
============================================================
Initializing Database Tables
============================================================

[1/3] Creating database tables...
✓ Tables created successfully

[2/3] Verifying tables...
✓ Found 3 tables:
  - audit_logs
  - sessions
  - users

[3/3] Verifying indexes...
✓ Created 11 indexes

============================================================
✓ Database initialization complete!
============================================================

Verifying database connection...
✓ PostgreSQL connected: PostgreSQL 16.x
✓ Found 3 tables in database

No users found. Creating default admin user...
✓ Created default admin user:
  Username: admin
  Password: admin
  ⚠ CHANGE THIS PASSWORD IN PRODUCTION!
```

---

## 📊 What Was Tested

The integration test (`test_db_integration.py`) validates:

1. ✅ **Table Creation**
   - Creates 3 tables: users, sessions, audit_logs
   - Verifies all tables exist
   - Checks indexes are created

2. ✅ **User Model**
   - Creates user with all fields
   - Tests UUID primary key
   - Validates role enum
   - Checks password hashing
   - Verifies timestamps

3. ✅ **Session Model**
   - Creates session linked to user
   - Tests foreign key relationship
   - Validates JSON context storage
   - Checks thread_id integration

4. ✅ **Audit Log Model**
   - Creates audit log for user action
   - Tests action enum
   - Validates JSON details
   - Checks IP address storage

5. ✅ **Relationships**
   - Loads user with related sessions
   - Loads user with related audit logs
   - Verifies one-to-many relationships

6. ✅ **Cascade Deletes**
   - Deletes user
   - Verifies sessions deleted
   - Verifies audit logs handling

7. ✅ **Cleanup**
   - Drops all tables
   - Closes connections

---

## 🗄️ Database Verification

### Connect to PostgreSQL

```bash
# Using docker-compose
docker-compose exec postgres psql -U admin -d guardianeye
```

### Useful SQL Commands

```sql
-- List all tables
\dt

-- Describe users table
\d users

-- View all users
SELECT username, email, role, is_active, created_at FROM users;

-- View sessions
SELECT id, user_id, title, is_active, created_at FROM sessions LIMIT 10;

-- View audit logs
SELECT action, user_id, success, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 20;

-- Count records
SELECT
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM sessions) as sessions,
  (SELECT COUNT(*) FROM audit_logs) as audit_logs;

-- Exit
\q
```

---

## 🧪 Manual Testing

### Test 1: Create a User Manually

```python
import asyncio
from src.db.postgres import get_postgres_connection
from src.db.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    engine = get_postgres_connection()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        user = User(
            username="testanalyst",
            email="analyst@test.com",
            hashed_password=pwd_context.hash("testpass"),
            role=UserRole.ANALYST,
            full_name="Test Analyst"
        )
        session.add(user)
        await session.commit()
        print(f"Created user: {user.username} (ID: {user.id})")

asyncio.run(create_test_user())
```

### Test 2: Query Users

```python
import asyncio
from sqlalchemy import select
from src.db.postgres import get_postgres_connection
from src.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async def list_users():
    engine = get_postgres_connection()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.role.value}")

asyncio.run(list_users())
```

### Test 3: Create Session and Audit Log

```python
import asyncio
from src.db.postgres import get_postgres_connection
from src.db.models import User, Session, AuditLog, AuditAction
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async def create_session_and_audit():
    engine = get_postgres_connection()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        # Get first user
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one()

        # Create session
        user_session = Session(
            user_id=user.id,
            title="Test Session",
            context={"test": "data"}
        )
        session.add(user_session)

        # Create audit log
        audit = AuditLog(
            user_id=user.id,
            action=AuditAction.QUERY_AGENT,
            details={"agent": "test"},
            ip_address="127.0.0.1"
        )
        session.add(audit)

        await session.commit()
        print(f"Created session and audit log for user: {user.username}")

asyncio.run(create_session_and_audit())
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"

**Cause:** PostgreSQL not running

**Solution:**
```bash
docker-compose up -d postgres
# Wait a few seconds
docker-compose ps  # Should show postgres as "Up"
```

### Issue: "Permission denied" (Docker)

**Cause:** User not in docker group

**Solution:**
```bash
# Option 1: Use sudo
sudo docker-compose up -d postgres

# Option 2: Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

### Issue: "Module not found: src"

**Cause:** PYTHONPATH not set

**Solution:**
```bash
# Always use PYTHONPATH when running scripts
PYTHONPATH=$(pwd) python test_db_integration.py
```

### Issue: Tables already exist error

**Cause:** Running tests multiple times

**Solution:**
The test script automatically cleans up, but if it crashed:
```bash
# Drop all tables manually
docker-compose exec postgres psql -U admin -d guardianeye -c "DROP TABLE IF EXISTS audit_logs, sessions, users CASCADE;"
```

### Issue: Can't connect to database

**Check .env file:**
```bash
cat .env | grep POSTGRES
# Should show:
# POSTGRES_URL=postgresql+asyncpg://admin:password@localhost:5432/guardianeye
```

**Test connection:**
```bash
docker-compose exec postgres psql -U admin -d guardianeye -c "SELECT 1;"
```

---

## ✅ Success Criteria

After testing, verify:

- [ ] PostgreSQL container running (`docker-compose ps`)
- [ ] Integration test passes (all 7 steps ✓)
- [ ] Tables created (users, sessions, audit_logs)
- [ ] 11 indexes created
- [ ] Can create users
- [ ] Can create sessions
- [ ] Can create audit logs
- [ ] Relationships work
- [ ] Cascade deletes work
- [ ] Default admin user created

---

## 📈 Next Steps After Testing

Once all tests pass:

1. ✅ **Phase 1 Complete** - Database integration working
2. ⏭️ **Phase 2** - Implement testing infrastructure
   - Create `docker-compose.test.yml`
   - Update `tests/conftest.py` with fixtures
   - Write comprehensive unit tests
   - Write integration tests
3. ⏭️ **Phase 3** - Update `seed_data.py` to seed users
4. ⏭️ **Phase 4** - Integrate with authentication service
5. ⏭️ **Phase 5** - Add session management to API
6. ⏭️ **Phase 6** - Implement audit logging in endpoints

---

## 📚 Related Documentation

- [DATABASE_IMPLEMENTATION.md](DATABASE_IMPLEMENTATION.md) - Full implementation details
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current progress
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Original plan
- [TODO.md](TODO.md) - Project TODO list

---

**Ready to test?** Start with Step 1 and work through the guide!

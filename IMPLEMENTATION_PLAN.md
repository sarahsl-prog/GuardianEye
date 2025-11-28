# Implementation Plan: Database Integration & Testing Infrastructure

**Date:** 2024-11-27
**Target:** TODO.md Items #2 (Database Integration) and #3 (Testing Infrastructure)
**Status:** Planning Phase

---

## 🎯 Objectives

### Phase 1: Database Integration (Critical Priority - P0)
1. Add PostgreSQL service to docker-compose.yml
2. Implement database models (User, Session, AuditLog)
3. Create database initialization and migrations
4. Test database connectivity and operations

### Phase 2: Testing Infrastructure (Critical Priority - P0)
5. Create docker-compose.test.yml for isolated test databases
6. Update conftest.py with database fixtures and setup/teardown
7. Configure pytest for local database testing
8. Implement test database seeding
9. Create helper utilities for test data

---

## 📋 Phase 1: Database Integration

### Task 1.1: Add PostgreSQL to docker-compose.yml

**Goal:** Add PostgreSQL 16 service with proper configuration

**Changes to make:**
```yaml
# docker-compose.yml additions
services:
  postgres:
    image: postgres:16-alpine
    container_name: guardianeye-postgres
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: guardianeye
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Acceptance Criteria:**
- [ ] PostgreSQL service defined
- [ ] Environment variables configured
- [ ] Volume persistence enabled
- [ ] Health checks implemented
- [ ] Service starts successfully

---

### Task 1.2: Implement Database Models

**File:** `src/db/models.py`

**Models to create:**

1. **User Model**
   - id (UUID, primary key)
   - username (unique, indexed)
   - email (unique, indexed)
   - hashed_password
   - role (admin, analyst, viewer)
   - is_active (boolean)
   - created_at, updated_at (timestamps)

2. **Session Model**
   - id (UUID, primary key)
   - user_id (foreign key to User)
   - thread_id (for conversation tracking)
   - context (JSON)
   - created_at, updated_at

3. **AuditLog Model**
   - id (UUID, primary key)
   - user_id (foreign key to User, nullable)
   - action (enum: login, query, agent_execution, etc.)
   - details (JSON)
   - ip_address
   - timestamp

**Technical Stack:**
- SQLAlchemy 2.0 with async support
- Alembic for migrations (optional, can use direct table creation)
- UUID for primary keys
- Proper indexes and constraints

**Acceptance Criteria:**
- [ ] All three models defined with proper fields
- [ ] Relationships configured
- [ ] Indexes created for performance
- [ ] Table creation tested

---

### Task 1.3: Database Initialization

**Files to create/update:**
- `src/db/init_db.py` - Database initialization
- Update `scripts/setup_db.py` - Include model table creation

**Functions needed:**
1. `create_tables()` - Create all tables
2. `init_database()` - Initialize database with base data
3. `verify_database()` - Health check for database

**Acceptance Criteria:**
- [ ] Tables created successfully
- [ ] Indexes created
- [ ] Foreign keys working
- [ ] Can insert and query data

---

### Task 1.4: Update seed_data.py for Users

**File:** `scripts/seed_data.py`

**Implement the seed_users() function:**
```python
async def seed_users():
    """Seed test users for development."""
    users = [
        {
            "username": "admin",
            "email": "admin@guardianeye.local",
            "password": "admin",  # Will be hashed
            "role": "admin",
        },
        {
            "username": "analyst",
            "email": "analyst@guardianeye.local",
            "password": "analyst",
            "role": "analyst",
        },
        {
            "username": "viewer",
            "email": "viewer@guardianeye.local",
            "password": "viewer",
            "role": "viewer",
        },
    ]
    # Implementation with password hashing
```

**Acceptance Criteria:**
- [ ] Users created in database
- [ ] Passwords properly hashed with bcrypt
- [ ] Roles assigned correctly
- [ ] Can authenticate with seeded users

---

## 📋 Phase 2: Testing Infrastructure

### Task 2.1: Create docker-compose.test.yml

**Goal:** Isolated test environment with separate databases

**File:** `docker-compose.test.yml`

**Services needed:**
```yaml
services:
  postgres-test:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
      POSTGRES_DB: guardianeye_test
    ports:
      - "5433:5432"  # Different port to avoid conflicts
    tmpfs:
      - /var/lib/postgresql/data  # Ephemeral - faster tests

  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"  # Different port
    tmpfs:
      - /data

  # Chroma test DB can use local directory
```

**Acceptance Criteria:**
- [ ] Test databases use different ports
- [ ] Data is ephemeral (tmpfs for speed)
- [ ] No conflicts with dev databases
- [ ] Can start/stop independently

---

### Task 2.2: Update conftest.py

**File:** `tests/conftest.py`

**Fixtures to add:**

```python
@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine."""
    # Create async engine for tests
    # Yield engine
    # Cleanup

@pytest.fixture(scope="function")
async def db_session(test_db_engine):
    """Create a new database session for a test."""
    # Create session
    # Setup tables
    # Yield session
    # Rollback and cleanup

@pytest.fixture(scope="session")
async def test_redis():
    """Redis client for tests."""
    # Connect to test Redis
    # Yield client
    # Cleanup

@pytest.fixture(scope="session")
def test_vector_store():
    """Vector store for tests."""
    # Create temporary Chroma DB
    # Yield store
    # Cleanup

@pytest.fixture
def mock_user(db_session):
    """Create a test user."""
    # Create and return test user

@pytest.fixture
def auth_headers(mock_user):
    """Get auth headers for API tests."""
    # Generate JWT token
    # Return headers dict
```

**Acceptance Criteria:**
- [ ] Database fixtures create/destroy cleanly
- [ ] Redis fixtures isolated per test
- [ ] Vector store uses temp directory
- [ ] Authentication fixtures working
- [ ] All fixtures properly scoped

---

### Task 2.3: Create Test Configuration

**File:** `tests/test_config.py`

**Settings for test environment:**
```python
TEST_POSTGRES_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5433/guardianeye_test"
TEST_REDIS_URL = "redis://localhost:6380/0"
TEST_CHROMA_DIR = "./data/chroma_test"
```

**Acceptance Criteria:**
- [ ] Test settings separated from production
- [ ] Easy to override via environment
- [ ] Well documented

---

### Task 2.4: Create Test Utilities

**File:** `tests/utils.py`

**Helper functions:**
```python
async def create_test_user(db_session, **kwargs):
    """Create a test user with defaults."""

async def create_test_session(db_session, user_id):
    """Create a test session."""

def get_test_jwt_token(user_data):
    """Generate JWT token for testing."""

async def seed_test_knowledge_base():
    """Seed minimal test knowledge base."""
```

**Acceptance Criteria:**
- [ ] Reusable test utilities created
- [ ] Well documented with examples
- [ ] Cover common test scenarios

---

### Task 2.5: Update pytest Configuration

**File:** `pyproject.toml`

**Update pytest settings:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term"
env = [
    "POSTGRES_URL=postgresql+asyncpg://test_user:test_pass@localhost:5433/guardianeye_test",
    "REDIS_URL=redis://localhost:6380/0",
    "CHROMA_PERSIST_DIRECTORY=./data/chroma_test",
    "APP_ENV=testing",
]
```

**Acceptance Criteria:**
- [ ] Test environment variables set
- [ ] Coverage configured
- [ ] Async tests properly configured

---

## 🧪 Testing Strategy

### Unit Tests to Update/Create

1. **Database Models Tests**
   - `tests/unit/test_db/test_models.py`
   - Test CRUD operations for each model
   - Test relationships
   - Test constraints and validation

2. **Database Connection Tests**
   - `tests/unit/test_db/test_postgres.py`
   - Test connection pooling
   - Test error handling

3. **Authentication Tests**
   - `tests/unit/test_services/test_auth_service.py`
   - Test user creation
   - Test password hashing
   - Test JWT generation

### Integration Tests to Create

1. **API with Database Tests**
   - `tests/integration/test_api/test_auth_integration.py`
   - Test login/logout with real database
   - Test session management

2. **Agent with Database Tests**
   - `tests/integration/test_agents/test_agent_with_db.py`
   - Test agent execution with audit logging

---

## 📝 Implementation Order

### Day 1: Database Setup
1. ✅ Update docker-compose.yml with PostgreSQL
2. ✅ Create database models in src/db/models.py
3. ✅ Create init_db.py for table creation
4. ✅ Update setup_db.py to initialize models
5. ✅ Test database connectivity

### Day 2: User Management
6. ✅ Implement seed_users() in seed_data.py
7. ✅ Update auth_service.py to use database
8. ✅ Test user creation and authentication
9. ✅ Create basic user CRUD operations

### Day 3: Testing Infrastructure
10. ✅ Create docker-compose.test.yml
11. ✅ Update conftest.py with database fixtures
12. ✅ Create test utilities
13. ✅ Configure pytest settings

### Day 4: Write Tests
14. ✅ Create database model tests
15. ✅ Create authentication integration tests
16. ✅ Create API integration tests with database
17. ✅ Run full test suite

### Day 5: Documentation & Verification
18. ✅ Update README.md with database setup instructions
19. ✅ Create TESTING.md guide
20. ✅ Run all tests and verify coverage
21. ✅ Update TODO.md

---

## 🔍 Acceptance Criteria (Overall)

### Database Integration
- [ ] PostgreSQL running in Docker
- [ ] All models created and tested
- [ ] Database initialization working
- [ ] User seeding functional
- [ ] Can perform CRUD operations
- [ ] Relationships working correctly
- [ ] Indexes created for performance

### Testing Infrastructure
- [ ] Test databases isolated from dev
- [ ] All fixtures working correctly
- [ ] Can run tests independently
- [ ] Tests clean up after themselves
- [ ] Test coverage > 80% for new code
- [ ] CI/CD ready (can run in pipeline)

### Code Quality
- [ ] All code follows project style
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Error handling robust
- [ ] Logging implemented

### Documentation
- [ ] README.md updated
- [ ] TESTING.md created
- [ ] API documentation current
- [ ] Code comments clear
- [ ] TODO.md updated

---

## 🚀 Getting Started

Once this plan is approved, we'll proceed with:

1. **Phase 1A**: Docker Compose & Database Models (Tasks 1.1, 1.2)
2. **Phase 1B**: Database Init & User Seeding (Tasks 1.3, 1.4)
3. **Phase 2A**: Test Infrastructure (Tasks 2.1, 2.2, 2.3)
4. **Phase 2B**: Test Utilities & Configuration (Tasks 2.4, 2.5)
5. **Phase 3**: Testing & Documentation (All remaining tasks)

**Estimated Time:** 2-3 days for full implementation and testing

**Dependencies:**
- Docker and Docker Compose installed
- PostgreSQL client tools (optional, for manual testing)
- All existing requirements.txt dependencies

---

## 📊 Success Metrics

After completion, we should have:

✅ **Database fully operational**
- PostgreSQL running
- Models working
- Users can be created
- Sessions tracked
- Audit logs captured

✅ **Testing infrastructure complete**
- Isolated test databases
- All fixtures working
- Test utilities available
- Tests passing
- Good coverage

✅ **Documentation updated**
- Setup instructions clear
- Testing guide complete
- API docs current

---

**Ready to proceed? Let's start with Phase 1A!**

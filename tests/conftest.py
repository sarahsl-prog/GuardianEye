"""Pytest configuration and fixtures."""

import os
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import redis.asyncio as aioredis

from src.main import app
from src.db.vector_store import get_vector_store

# Try to import database models, but don't fail if they're not implemented yet
try:
    from src.db.models import Base, User, Session as DBSession, AuditLog, UserRole
    DB_MODELS_AVAILABLE = True
except (ImportError, AttributeError):
    DB_MODELS_AVAILABLE = False
    Base = User = DBSession = AuditLog = UserRole = None


# Test database configuration
TEST_POSTGRES_URL = os.getenv(
    "TEST_POSTGRES_URL",
    "postgresql+asyncpg://test_user:test_pass@localhost:5433/guardianeye_test"
)
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6380/0")
TEST_CHROMA_DIR = os.getenv("TEST_CHROMA_DIR", "./data/chroma_test")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_engine():
    """
    Create test database engine for the session.

    This engine is reused across all tests in the session for performance.
    Individual tests get their own transaction that is rolled back.
    """
    if not DB_MODELS_AVAILABLE:
        pytest.skip("Database models not implemented yet")

    engine = create_async_engine(
        TEST_POSTGRES_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for a test.

    Each test gets a fresh session with its own transaction that is
    rolled back after the test completes, ensuring test isolation.

    Yields:
        AsyncSession: Database session for the test
    """
    # Create async session maker
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Rollback after test
            await session.rollback()


@pytest.fixture(scope="session")
async def test_redis():
    """
    Redis client for tests.

    Provides a Redis client connected to the test Redis instance.
    The database is flushed before and after the test session.

    Yields:
        Redis: Async Redis client
    """
    redis_client = await aioredis.from_url(
        TEST_REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    # Clear test database before tests
    await redis_client.flushdb()

    yield redis_client

    # Clear test database after tests
    await redis_client.flushdb()
    await redis_client.aclose()


@pytest.fixture
async def redis_client(test_redis):
    """
    Per-test Redis client that clears its data after each test.

    Yields:
        Redis: Async Redis client
    """
    yield test_redis
    # Clear all keys after each test
    await test_redis.flushdb()


@pytest.fixture(scope="session")
def test_vector_store_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test vector store.

    Yields:
        Path: Path to temporary Chroma directory
    """
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="chroma_test_"))

    yield temp_dir

    # Cleanup after all tests
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def vector_store(test_vector_store_dir, monkeypatch):
    """
    Vector store for tests.

    Creates a fresh Chroma vector store for each test using a
    temporary directory that is cleaned up after the test.

    Args:
        test_vector_store_dir: Temporary directory for test vector store
        monkeypatch: Pytest monkeypatch fixture for mocking

    Returns:
        Chroma: Vector store instance
    """
    # Mock the persist directory to use test directory
    monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", str(test_vector_store_dir))

    # Get vector store (will use mocked directory)
    store = get_vector_store()

    return store


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_agent_request():
    """Sample agent request for testing."""
    return {
        "query": "Test query",
        "context": {"test": "data"},
        "session_id": "test_session_123"
    }


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """
    Create a test user in the database.

    Args:
        db_session: Database session

    Returns:
        User: Test user instance
    """
    if not DB_MODELS_AVAILABLE:
        pytest.skip("Database models not implemented yet")

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        username="testuser",
        email="testuser@test.com",
        hashed_password=pwd_context.hash("testpass123"),
        role=UserRole.ANALYST,
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession):
    """
    Create a test admin user in the database.

    Args:
        db_session: Database session

    Returns:
        User: Test admin user instance
    """
    if not DB_MODELS_AVAILABLE:
        pytest.skip("Database models not implemented yet")

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        username="testadmin",
        email="testadmin@test.com",
        hashed_password=pwd_context.hash("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """
    Get authentication headers for API tests.

    Args:
        test_user: Test user instance

    Returns:
        dict: Headers with JWT token
    """
    if not DB_MODELS_AVAILABLE:
        pytest.skip("Database models not implemented yet")

    from datetime import timedelta
    from src.services.auth_service import AuthService

    auth_service = AuthService()
    token = auth_service.create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_llm():
    """
    Mock LLM for testing.

    Provides a mock language model that simulates LLM behavior without
    making actual API calls. Useful for unit tests that need to test
    agent logic without external dependencies.

    Returns:
        MagicMock: A mock LLM instance with common methods mocked
    """
    llm = MagicMock()

    # Mock model name
    llm.model_name = "mock-model"

    # Mock synchronous invoke
    llm.invoke.return_value = AIMessage(
        content="This is a mock response from the LLM."
    )

    # Mock asynchronous invoke
    async def mock_ainvoke(*args, **kwargs):
        return AIMessage(content="This is a mock async response from the LLM.")

    llm.ainvoke = AsyncMock(side_effect=mock_ainvoke)

    # Mock streaming
    async def mock_astream(*args, **kwargs):
        chunks = ["This ", "is ", "a ", "mock ", "streaming ", "response."]
        for chunk in chunks:
            yield chunk

    llm.astream = mock_astream

    # Mock batch processing
    async def mock_abatch(inputs, **kwargs):
        return [
            AIMessage(content=f"Mock response for input: {inp}")
            for inp in inputs
        ]

    llm.abatch = AsyncMock(side_effect=mock_abatch)

    # Mock other common attributes
    llm.temperature = 0.7
    llm.max_tokens = 1000

    return llm


@pytest.fixture
def mock_llm_with_error():
    """
    Mock LLM that raises errors for testing error handling.

    Returns:
        MagicMock: A mock LLM instance that raises exceptions
    """
    llm = MagicMock()
    llm.model_name = "mock-error-model"
    llm.invoke.side_effect = Exception("Mock LLM error")
    llm.ainvoke = AsyncMock(side_effect=Exception("Mock async LLM error"))

    return llm

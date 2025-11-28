"""Test utility functions and helpers."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.db.models import User, Session as DBSession, AuditLog, UserRole, AuditAction


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_user(
    db_session: AsyncSession,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpass123",
    role: UserRole = UserRole.ANALYST,
    is_active: bool = True,
    **kwargs
) -> User:
    """
    Create a test user with default or custom values.

    Args:
        db_session: Database session
        username: User's username
        email: User's email
        password: Plain text password (will be hashed)
        role: User's role
        is_active: Whether user is active
        **kwargs: Additional user attributes

    Returns:
        User: Created user instance
    """
    user = User(
        username=username,
        email=email,
        hashed_password=pwd_context.hash(password),
        role=role,
        is_active=is_active,
        **kwargs
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


async def create_test_session(
    db_session: AsyncSession,
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    title: str = "Test Session",
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> DBSession:
    """
    Create a test session with default or custom values.

    Args:
        db_session: Database session
        user_id: User ID (if None, will create a new user)
        thread_id: LangGraph thread ID
        title: Session title
        context: Session context data
        **kwargs: Additional session attributes

    Returns:
        DBSession: Created session instance
    """
    # Create user if not provided
    if user_id is None:
        test_user = await create_test_user(db_session)
        user_id = test_user.id

    # Generate thread_id if not provided
    if thread_id is None:
        thread_id = f"thread_{uuid4().hex[:12]}"

    # Default context
    if context is None:
        context = {"agent": "test_agent", "status": "active"}

    session = DBSession(
        user_id=user_id,
        thread_id=thread_id,
        title=title,
        context=context,
        **kwargs
    )

    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return session


async def create_test_audit_log(
    db_session: AsyncSession,
    user_id: Optional[str] = None,
    action: AuditAction = AuditAction.QUERY,
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1",
    user_agent: Optional[str] = None,
    success: bool = True,
    **kwargs
) -> AuditLog:
    """
    Create a test audit log entry with default or custom values.

    Args:
        db_session: Database session
        user_id: User ID (can be None for system actions)
        action: Audit action type
        details: Action details
        ip_address: IP address of the action
        user_agent: User agent string
        success: Whether the action was successful
        **kwargs: Additional audit log attributes

    Returns:
        AuditLog: Created audit log instance
    """
    # Default details
    if details is None:
        details = {"test": "data", "action": action.value}

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        **kwargs
    )

    db_session.add(audit_log)
    await db_session.commit()
    await db_session.refresh(audit_log)

    return audit_log


def get_test_jwt_token(
    username: str = "testuser",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT token for testing.

    Args:
        username: Username to encode in token
        expires_delta: Token expiration time

    Returns:
        str: JWT token
    """
    from src.services.auth_service import AuthService

    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    auth_service = AuthService()
    token = auth_service.create_access_token(
        data={"sub": username},
        expires_delta=expires_delta
    )

    return token


def get_test_auth_headers(
    username: str = "testuser",
    expires_delta: Optional[timedelta] = None
) -> Dict[str, str]:
    """
    Get authentication headers for API testing.

    Args:
        username: Username to encode in token
        expires_delta: Token expiration time

    Returns:
        dict: Headers with Authorization bearer token
    """
    token = get_test_jwt_token(username, expires_delta)
    return {"Authorization": f"Bearer {token}"}


async def seed_test_knowledge_base(vector_store, num_docs: int = 5):
    """
    Seed a minimal test knowledge base with sample documents.

    Args:
        vector_store: Vector store instance
        num_docs: Number of test documents to add

    Returns:
        list: List of added document IDs
    """
    from langchain.schema import Document

    documents = []
    for i in range(num_docs):
        doc = Document(
            page_content=f"Test security document {i + 1}. "
                         f"This contains information about security topic {i + 1}.",
            metadata={
                "source": f"test_doc_{i + 1}.md",
                "category": "security",
                "topic": f"topic_{i + 1}",
                "test": True
            }
        )
        documents.append(doc)

    # Add documents to vector store
    ids = vector_store.add_documents(documents)

    return ids


async def cleanup_test_data(db_session: AsyncSession):
    """
    Clean up all test data from the database.

    This is useful for cleaning up after tests that don't use
    transactions (e.g., some integration tests).

    Args:
        db_session: Database session
    """
    from sqlalchemy import delete

    # Delete in reverse order of foreign key dependencies
    await db_session.execute(delete(AuditLog))
    await db_session.execute(delete(DBSession))
    await db_session.execute(delete(User))

    await db_session.commit()


def assert_dict_contains(actual: Dict, expected: Dict):
    """
    Assert that actual dict contains all key-value pairs from expected dict.

    This is useful for testing API responses where you only care about
    certain fields.

    Args:
        actual: The actual dictionary
        expected: Dictionary with expected key-value pairs

    Raises:
        AssertionError: If any expected key-value pair is not in actual
    """
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, \
            f"Key '{key}': expected {value}, got {actual[key]}"


def assert_response_success(response, status_code: int = 200):
    """
    Assert that an API response is successful.

    Args:
        response: Response object
        status_code: Expected status code

    Raises:
        AssertionError: If response is not successful
    """
    assert response.status_code == status_code, \
        f"Expected status {status_code}, got {response.status_code}. " \
        f"Response: {response.json() if response.text else 'No content'}"


def create_mock_agent_request(
    query: str = "Test query",
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a mock agent request for testing.

    Args:
        query: Query string
        context: Context data
        session_id: Session ID

    Returns:
        dict: Mock agent request
    """
    request = {"query": query}

    if context is not None:
        request["context"] = context

    if session_id is not None:
        request["session_id"] = session_id

    return request

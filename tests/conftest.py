"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


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
def mock_llm():
    """Mock LLM for testing."""
    # TODO: Implement mock LLM
    pass

"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage

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

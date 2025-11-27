"""WebSocket endpoint integration tests."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
def test_websocket_unknown_agent(mock_llm, client):
    """Test WebSocket connection with unknown agent name."""
    with client.websocket_connect("/api/v1/ws/agent/unknown_agent") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "Unknown agent" in data["content"]
        assert "available_agents" in data


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
@patch("src.api.v1.websocket.IncidentTriageAgent")
def test_websocket_valid_agent_connection(mock_agent_class, mock_llm, client):
    """Test WebSocket connection with valid agent."""
    # Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Mock agent
    mock_agent = MagicMock()
    mock_agent.get_prompt_template.return_value = "Test prompt: {query}"
    mock_agent_class.return_value = mock_agent

    with client.websocket_connect("/api/v1/ws/agent/incident_triage") as websocket:
        # Receive connection acknowledgment
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["agent"] == "incident_triage"


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
@patch("src.api.v1.websocket.IncidentTriageAgent")
def test_websocket_invalid_json(mock_agent_class, mock_llm, client):
    """Test WebSocket with invalid JSON payload."""
    # Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Mock agent
    mock_agent = MagicMock()
    mock_agent.get_prompt_template.return_value = "Test prompt: {query}"
    mock_agent_class.return_value = mock_agent

    with client.websocket_connect("/api/v1/ws/agent/incident_triage") as websocket:
        # Receive connection acknowledgment
        data = websocket.receive_json()
        assert data["type"] == "connected"

        # Send invalid JSON
        websocket.send_text("not valid json")

        # Should receive error
        error_data = websocket.receive_json()
        assert error_data["type"] == "error"
        assert "Invalid JSON" in error_data["content"]


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
@patch("src.api.v1.websocket.IncidentTriageAgent")
def test_websocket_missing_query(mock_agent_class, mock_llm, client):
    """Test WebSocket with missing query field."""
    # Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Mock agent
    mock_agent = MagicMock()
    mock_agent.get_prompt_template.return_value = "Test prompt: {query}"
    mock_agent_class.return_value = mock_agent

    with client.websocket_connect("/api/v1/ws/agent/incident_triage") as websocket:
        # Receive connection acknowledgment
        data = websocket.receive_json()
        assert data["type"] == "connected"

        # Send request without query
        websocket.send_json({"context": {}})

        # Should receive error
        error_data = websocket.receive_json()
        assert error_data["type"] == "error"
        assert "Missing 'query'" in error_data["content"]


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
@patch("src.api.v1.websocket.ThreatHuntingAgent")
def test_websocket_streaming_response(mock_agent_class, mock_llm, client):
    """Test WebSocket streaming response."""
    # Mock LLM with streaming response
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Mock agent
    mock_agent = MagicMock()
    mock_agent.get_prompt_template.return_value = "Test prompt: {query}"
    mock_agent_class.return_value = mock_agent

    # Create async generator for streaming
    async def mock_stream(*args, **kwargs):
        chunks = ["Hello", " ", "world", "!"]
        for chunk in chunks:
            yield chunk

    # Mock the chain's astream method
    with patch("src.api.v1.websocket.ChatPromptTemplate") as mock_prompt_class:
        mock_prompt = MagicMock()
        mock_prompt_class.from_template.return_value = mock_prompt

        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.astream = mock_stream

        # Set up the chain creation
        mock_prompt.__or__ = MagicMock(return_value=MagicMock())
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)

        with client.websocket_connect("/api/v1/ws/agent/threat_hunting") as websocket:
            # Receive connection acknowledgment
            data = websocket.receive_json()
            assert data["type"] == "connected"

            # Send query
            websocket.send_json({
                "query": "Analyze threat indicators",
                "session_id": "test_123"
            })

            # Receive start message
            start_data = websocket.receive_json()
            assert start_data["type"] == "start"

            # Receive chunks
            chunks_received = []
            while True:
                chunk_data = websocket.receive_json()
                if chunk_data["type"] == "chunk":
                    chunks_received.append(chunk_data["content"])
                elif chunk_data["type"] == "end":
                    assert chunk_data["content"] == "Response complete"
                    assert "metadata" in chunk_data
                    break

            # Verify we received chunks
            assert len(chunks_received) == 4
            assert "".join(chunks_received) == "Hello world!"


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
@patch("src.api.v1.websocket.SecurityKnowledgeAgent")
def test_websocket_with_context(mock_agent_class, mock_llm, client):
    """Test WebSocket with additional context."""
    # Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Mock agent
    mock_agent = MagicMock()
    mock_agent.get_prompt_template.return_value = "Test prompt: {query} {alert_details}"
    mock_agent_class.return_value = mock_agent

    # Create async generator for streaming
    async def mock_stream(*args, **kwargs):
        # Verify context was passed
        assert "alert_details" in kwargs
        yield "Response"

    with patch("src.api.v1.websocket.ChatPromptTemplate") as mock_prompt_class:
        mock_prompt = MagicMock()
        mock_prompt_class.from_template.return_value = mock_prompt

        mock_chain = MagicMock()
        mock_chain.astream = mock_stream

        mock_prompt.__or__ = MagicMock(return_value=MagicMock())
        mock_prompt.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)

        with client.websocket_connect("/api/v1/ws/agent/security_knowledge") as websocket:
            # Receive connection acknowledgment
            data = websocket.receive_json()
            assert data["type"] == "connected"

            # Send query with context
            websocket.send_json({
                "query": "Analyze security alert",
                "context": {"alert_details": "Suspicious login attempt"},
                "session_id": "test_456"
            })

            # Receive start message
            start_data = websocket.receive_json()
            assert start_data["type"] == "start"
            assert start_data["metadata"]["session_id"] == "test_456"


@patch("src.api.v1.websocket.LLMFactory.get_default_llm")
def test_websocket_all_agents(mock_llm, client):
    """Test that all agents in registry are accessible."""
    from src.api.v1.websocket import AGENT_REGISTRY

    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    for agent_name in AGENT_REGISTRY.keys():
        with client.websocket_connect(f"/api/v1/ws/agent/{agent_name}") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["agent"] == agent_name

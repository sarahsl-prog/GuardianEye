"""Integration tests for full multi-agent orchestration."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import AIMessage

from src.services.agent_service import AgentService


@pytest.mark.asyncio
async def test_agent_service_executes_main_graph():
    """Test that AgentService executes the main graph."""
    with patch("src.services.agent_service.create_main_graph") as mock_create_graph, \
         patch("src.services.agent_service.get_checkpointer") as mock_checkpointer, \
         patch("src.services.agent_service.get_vector_store") as mock_vector_store:

        # Mock graph
        mock_graph = AsyncMock()
        mock_result = {
            "final_result": "Test result from agent",
            "execution_path": ["main_supervisor -> security_ops_team", "security_ops_team", "incident_triage"],
            "current_team": "security_ops_team",
            "current_agent": "incident_triage",
            "total_tokens": 100,
            "start_time": 0.0,
            "messages": [AIMessage(content="Test response")]
        }
        mock_graph.ainvoke = AsyncMock(return_value=mock_result)
        mock_create_graph.return_value = mock_graph

        # Mock checkpointer
        mock_checkpointer.return_value = None

        # Mock vector store
        mock_vector_store.return_value = MagicMock()

        # Execute
        service = AgentService()
        result = await service.execute_query(
            query="Analyze this security incident",
            user_id="test_user",
            session_id="test_session"
        )

        # Verify
        assert result["result"] == "Test result from agent"
        assert "security_ops_team" in result["execution_path"]
        assert "incident_triage" in result["execution_path"]
        assert result["metadata"]["team"] == "security_ops_team"


@pytest.mark.asyncio
async def test_agent_service_handles_errors():
    """Test that AgentService handles errors gracefully."""
    with patch("src.services.agent_service.create_main_graph") as mock_create_graph, \
         patch("src.services.agent_service.get_checkpointer") as mock_checkpointer:

        # Mock graph to raise error
        mock_graph = AsyncMock()
        mock_graph.ainvoke = AsyncMock(side_effect=Exception("Test error"))
        mock_create_graph.return_value = mock_graph
        mock_checkpointer.return_value = None

        # Execute
        service = AgentService()
        result = await service.execute_query(
            query="Test query",
            user_id="test_user"
        )

        # Verify error handling
        assert "error" in result
        assert "Error executing query" in result["result"]


@pytest.mark.asyncio
async def test_api_execute_endpoint_uses_agent_service(client):
    """Test that /execute endpoint uses AgentService for orchestration."""
    with patch("src.services.agent_service.AgentService") as MockAgentService:
        # Mock service
        mock_service = AsyncMock()
        mock_service.execute_query = AsyncMock(return_value={
            "result": "Security incident analyzed and triaged",
            "execution_path": ["main_supervisor -> security_ops_team", "security_ops_team", "incident_triage"],
            "execution_time": 1.5,
            "session_id": "test_session",
            "metadata": {
                "user_id": "anonymous",
                "team": "security_ops_team",
                "agent": "incident_triage",
                "tokens": 150
            }
        })
        MockAgentService.return_value = mock_service

        # Call API
        response = client.post(
            "/api/v1/agents/execute",
            json={
                "query": "Analyze security incident from IP 192.168.1.100",
                "session_id": "test_session"
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "Security incident analyzed" in data["result"]
        assert "security_ops_team" in data["execution_path"]
        assert "incident_triage" in data["execution_path"]
        assert data["execution_time"] == 1.5

        # Verify service was called
        mock_service.execute_query.assert_called_once()


@pytest.mark.asyncio
async def test_end_to_end_incident_workflow(client):
    """Test complete incident response workflow through orchestration."""
    with patch("src.services.agent_service.AgentService") as MockAgentService:
        mock_service = AsyncMock()
        mock_service.execute_query = AsyncMock(return_value={
            "result": "Incident triaged: HIGH severity, requires immediate response",
            "execution_path": [
                "main_supervisor -> security_ops_team",
                "security_ops_team",
                "incident_triage"
            ],
            "execution_time": 2.1,
            "session_id": "incident_session_1",
            "metadata": {
                "user_id": "analyst1",
                "team": "security_ops_team",
                "agent": "incident_triage",
                "tokens": 200,
                "severity": "HIGH"
            }
        })
        MockAgentService.return_value = mock_service

        response = client.post(
            "/api/v1/agents/execute",
            json={
                "query": "Multiple failed login attempts from suspicious IP",
                "context": {"ip": "192.168.1.100", "attempts": 50},
                "session_id": "incident_session_1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "HIGH severity" in data["result"]
        assert data["metadata"]["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_end_to_end_threat_hunting_workflow(client):
    """Test threat hunting workflow through orchestration."""
    with patch("src.services.agent_service.AgentService") as MockAgentService:
        mock_service = AsyncMock()
        mock_service.execute_query = AsyncMock(return_value={
            "result": "Generated 5 threat hunting hypotheses for potential data exfiltration",
            "execution_path": [
                "main_supervisor -> threat_intel_team",
                "threat_intel_team",
                "threat_hunting"
            ],
            "execution_time": 3.2,
            "session_id": "threat_session_1",
            "metadata": {
                "user_id": "analyst2",
                "team": "threat_intel_team",
                "agent": "threat_hunting",
                "tokens": 300,
                "hypotheses_count": 5
            }
        })
        MockAgentService.return_value = mock_service

        response = client.post(
            "/api/v1/agents/execute",
            json={
                "query": "Generate threat hunting hypotheses for data exfiltration",
                "session_id": "threat_session_1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "threat hunting hypotheses" in data["result"]
        assert "threat_intel_team" in data["execution_path"]


@pytest.mark.asyncio
async def test_end_to_end_compliance_workflow(client):
    """Test compliance audit workflow through orchestration."""
    with patch("src.services.agent_service.AgentService") as MockAgentService:
        mock_service = AsyncMock()
        mock_service.execute_query = AsyncMock(return_value={
            "result": "NIST CSF compliance audit complete: 85% compliant",
            "execution_path": [
                "main_supervisor -> governance_team",
                "governance_team",
                "compliance_auditor"
            ],
            "execution_time": 4.5,
            "session_id": "compliance_session_1",
            "metadata": {
                "user_id": "auditor1",
                "team": "governance_team",
                "agent": "compliance_auditor",
                "tokens": 400,
                "compliance_score": 85
            }
        })
        MockAgentService.return_value = mock_service

        response = client.post(
            "/api/v1/agents/execute",
            json={
                "query": "Audit our systems against NIST Cybersecurity Framework",
                "context": {"framework": "NIST CSF"},
                "session_id": "compliance_session_1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "compliance audit" in data["result"].lower()
        assert "governance_team" in data["execution_path"]


@pytest.mark.asyncio
async def test_execution_path_hierarchy(client):
    """Test that execution path shows proper hierarchy."""
    with patch("src.services.agent_service.AgentService") as MockAgentService:
        mock_service = AsyncMock()
        mock_service.execute_query = AsyncMock(return_value={
            "result": "Test result",
            "execution_path": [
                "main_supervisor -> security_ops_team",
                "security_ops_team",
                "incident_triage"
            ],
            "execution_time": 1.0,
            "session_id": "test",
            "metadata": {}
        })
        MockAgentService.return_value = mock_service

        response = client.post(
            "/api/v1/agents/execute",
            json={"query": "test"}
        )

        data = response.json()
        path = data["execution_path"]

        # Verify hierarchy: Main Supervisor → Team → Specialist
        assert "main_supervisor" in path[0]
        assert "security_ops_team" in path[0]
        assert "security_ops_team" in path[1]
        assert "incident_triage" in path[2]

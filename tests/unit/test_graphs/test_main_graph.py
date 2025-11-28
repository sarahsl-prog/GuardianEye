"""Unit tests for main graph orchestration."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.graphs.main_graph import (
    create_main_graph,
    main_supervisor_node,
    security_ops_team_node,
    threat_intel_team_node,
    governance_team_node,
    route_to_team
)
from src.core.state import GuardianEyeState


@pytest.fixture
def base_state() -> GuardianEyeState:
    """Create a base state for testing."""
    return {
        "messages": [HumanMessage(content="Test security incident")],
        "user_id": "test_user",
        "session_id": "test_session",
        "current_team": None,
        "current_agent": None,
        "next_action": None,
        "intermediate_results": {},
        "final_result": None,
        "execution_path": [],
        "tool_calls": [],
        "total_tokens": 0,
        "start_time": 0.0,
        "errors": []
    }


def test_create_main_graph():
    """Test that main graph can be created successfully."""
    graph = create_main_graph()
    assert graph is not None


def test_route_to_team_with_security_ops(base_state):
    """Test routing to security ops team."""
    base_state["current_team"] = "security_ops_team"
    result = route_to_team(base_state)
    assert result == "security_ops_team"


def test_route_to_team_with_threat_intel(base_state):
    """Test routing to threat intel team."""
    base_state["current_team"] = "threat_intel_team"
    result = route_to_team(base_state)
    assert result == "threat_intel_team"


def test_route_to_team_with_governance(base_state):
    """Test routing to governance team."""
    base_state["current_team"] = "governance_team"
    result = route_to_team(base_state)
    assert result == "governance_team"


def test_route_to_team_with_finish(base_state):
    """Test routing to END when finished."""
    base_state["current_team"] = "FINISH"
    result = route_to_team(base_state)
    assert result == "__end__"


def test_route_to_team_with_none(base_state):
    """Test routing to END when current_team is None."""
    base_state["current_team"] = None
    result = route_to_team(base_state)
    assert result == "__end__"


@pytest.mark.asyncio
async def test_main_supervisor_node_routes_to_team(base_state, mock_llm):
    """Test main supervisor node routes to appropriate team."""
    # Mock the supervisor to route to security ops
    with patch("src.agents.graphs.main_graph.MainSupervisor") as MockSupervisor:
        mock_supervisor_instance = AsyncMock()
        mock_supervisor_instance.route = AsyncMock(return_value="security_ops_team")
        MockSupervisor.return_value = mock_supervisor_instance

        result = await main_supervisor_node(base_state)

        assert result["current_team"] == "security_ops_team"
        assert "main_supervisor -> security_ops_team" in result["execution_path"]
        # Routing message is added
        assert any("Routing to security_ops_team" in str(msg.content) for msg in result["messages"])


@pytest.mark.asyncio
async def test_main_supervisor_node_finishes(base_state, mock_llm):
    """Test main supervisor node can finish."""
    with patch("src.agents.graphs.main_graph.MainSupervisor") as MockSupervisor:
        mock_supervisor_instance = AsyncMock()
        mock_supervisor_instance.route = AsyncMock(return_value="FINISH")
        MockSupervisor.return_value = mock_supervisor_instance

        result = await main_supervisor_node(base_state)

        assert result["current_team"] is None
        assert "main_supervisor -> FINISH" in result["execution_path"]


@pytest.mark.asyncio
async def test_security_ops_team_node_executes_subgraph(base_state):
    """Test security ops team node executes subgraph."""
    # Mock the subgraph - patch where it's imported
    with patch("src.agents.graphs.security_ops_graph.create_security_ops_graph") as mock_create:
        mock_graph = AsyncMock()
        mock_result_state = base_state.copy()
        mock_result_state["final_result"] = "Incident triaged successfully"
        mock_result_state["execution_path"] = ["incident_triage"]
        mock_graph.ainvoke = AsyncMock(return_value=mock_result_state)
        mock_create.return_value = mock_graph

        result = await security_ops_team_node(base_state)

        # Verify subgraph was called
        mock_graph.ainvoke.assert_called_once_with(base_state)

        # Verify execution path includes team
        assert "security_ops_team" in result["execution_path"]
        assert result["final_result"] == "Incident triaged successfully"


@pytest.mark.asyncio
async def test_threat_intel_team_node_executes_subgraph(base_state):
    """Test threat intel team node executes subgraph."""
    with patch("src.agents.graphs.threat_intel_graph.create_threat_intel_graph") as mock_create:
        mock_graph = AsyncMock()
        mock_result_state = base_state.copy()
        mock_result_state["final_result"] = "Threat hunting complete"
        mock_result_state["execution_path"] = ["threat_hunting"]
        mock_graph.ainvoke = AsyncMock(return_value=mock_result_state)
        mock_create.return_value = mock_graph

        result = await threat_intel_team_node(base_state)

        mock_graph.ainvoke.assert_called_once_with(base_state)
        assert "threat_intel_team" in result["execution_path"]
        assert result["final_result"] == "Threat hunting complete"


@pytest.mark.asyncio
async def test_governance_team_node_executes_subgraph(base_state):
    """Test governance team node executes subgraph."""
    with patch("src.agents.graphs.governance_graph.create_governance_graph") as mock_create:
        mock_graph = AsyncMock()
        mock_result_state = base_state.copy()
        mock_result_state["final_result"] = "Compliance audit complete"
        mock_result_state["execution_path"] = ["compliance_auditor"]
        mock_graph.ainvoke = AsyncMock(return_value=mock_result_state)
        mock_create.return_value = mock_graph

        result = await governance_team_node(base_state)

        mock_graph.ainvoke.assert_called_once_with(base_state)
        assert "governance_team" in result["execution_path"]
        assert result["final_result"] == "Compliance audit complete"


@pytest.mark.asyncio
async def test_full_graph_execution_security_ops(base_state):
    """Test full graph execution routes to security ops."""
    # This is an integration-style test but checks the full flow
    with patch("src.agents.graphs.main_graph.MainSupervisor") as MockSupervisor, \
         patch("src.agents.graphs.security_ops_graph.create_security_ops_graph") as mock_create_sec_ops:

        # Mock supervisor to route to security ops
        mock_supervisor = AsyncMock()
        mock_supervisor.route = AsyncMock(return_value="security_ops_team")
        MockSupervisor.return_value = mock_supervisor

        # Mock security ops subgraph
        mock_sec_ops_graph = AsyncMock()
        mock_result = base_state.copy()
        mock_result["final_result"] = "Security incident handled"
        mock_result["execution_path"] = ["incident_triage"]
        mock_sec_ops_graph.ainvoke = AsyncMock(return_value=mock_result)
        mock_create_sec_ops.return_value = mock_sec_ops_graph

        # Create and execute graph
        graph = create_main_graph()
        result = await graph.ainvoke(base_state)

        # Verify routing happened
        assert "security_ops_team" in result["execution_path"]
        assert result["final_result"] == "Security incident handled"


@pytest.mark.asyncio
async def test_execution_path_tracking(base_state):
    """Test that execution path is properly tracked through the hierarchy."""
    with patch("src.agents.graphs.main_graph.MainSupervisor") as MockSupervisor, \
         patch("src.agents.graphs.threat_intel_graph.create_threat_intel_graph") as mock_create:

        # Mock supervisor
        mock_supervisor = AsyncMock()
        mock_supervisor.route = AsyncMock(return_value="threat_intel_team")
        MockSupervisor.return_value = mock_supervisor

        # Mock threat intel graph - preserve execution path from input state
        mock_graph = AsyncMock()

        async def mock_ainvoke(state):
            """Mock that preserves and appends to execution path."""
            result = state.copy()
            result["execution_path"].append("threat_hunting")
            result["final_result"] = "Threats identified"
            return result

        mock_graph.ainvoke = mock_ainvoke
        mock_create.return_value = mock_graph

        # Execute
        graph = create_main_graph()
        result = await graph.ainvoke(base_state)

        # Verify execution path shows hierarchy
        assert "main_supervisor -> threat_intel_team" in result["execution_path"]
        assert "threat_hunting" in result["execution_path"]
        assert "threat_intel_team" in result["execution_path"]

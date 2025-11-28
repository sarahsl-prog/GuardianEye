"""Main orchestration graph for GuardianEye."""

from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph

from src.agents.supervisors.main_supervisor import MainSupervisor
from src.core.llm_factory import LLMFactory
from src.core.state import GuardianEyeState


async def main_supervisor_node(state: GuardianEyeState):
    """Main supervisor node that routes to team supervisors."""
    llm = LLMFactory.get_default_llm()
    supervisor = MainSupervisor(llm)

    # Route to appropriate team
    next_team = await supervisor.route(state)

    # Update state
    state["current_team"] = next_team if next_team != "FINISH" else None
    state["execution_path"].append(f"main_supervisor -> {next_team}")

    # Add routing message
    if next_team != "FINISH":
        state["messages"].append(
            AIMessage(content=f"Routing to {next_team}")
        )

    return state


async def security_ops_team_node(state: GuardianEyeState):
    """Security operations team node - executes security ops subgraph."""
    from src.agents.graphs.security_ops_graph import create_security_ops_graph

    # Create and execute the security ops subgraph
    security_ops_graph = create_security_ops_graph()

    # Execute subgraph with current state
    result_state = await security_ops_graph.ainvoke(state)

    # Update execution path
    result_state["execution_path"].append("security_ops_team")

    return result_state


async def threat_intel_team_node(state: GuardianEyeState):
    """Threat intelligence team node - executes threat intel subgraph."""
    from src.agents.graphs.threat_intel_graph import create_threat_intel_graph

    # Create and execute the threat intel subgraph
    threat_intel_graph = create_threat_intel_graph()

    # Execute subgraph with current state
    result_state = await threat_intel_graph.ainvoke(state)

    # Update execution path
    result_state["execution_path"].append("threat_intel_team")

    return result_state


async def governance_team_node(state: GuardianEyeState):
    """Governance team node - executes governance subgraph."""
    from src.agents.graphs.governance_graph import create_governance_graph

    # Create and execute the governance subgraph
    governance_graph = create_governance_graph()

    # Execute subgraph with current state
    result_state = await governance_graph.ainvoke(state)

    # Update execution path
    result_state["execution_path"].append("governance_team")

    return result_state


def route_to_team(state: GuardianEyeState) -> Literal["security_ops_team", "threat_intel_team", "governance_team", "__end__"]:
    """Route to the appropriate team based on supervisor decision."""
    current_team = state.get("current_team")

    if current_team is None or current_team == "FINISH":
        return "__end__"

    return current_team  # type: ignore


def create_main_graph():
    """
    Create the main orchestration graph.

    Returns:
        Compiled StateGraph for main orchestration
    """
    # Create graph
    workflow = StateGraph(GuardianEyeState)

    # Add nodes
    workflow.add_node("main_supervisor", main_supervisor_node)
    workflow.add_node("security_ops_team", security_ops_team_node)
    workflow.add_node("threat_intel_team", threat_intel_team_node)
    workflow.add_node("governance_team", governance_team_node)

    # Set entry point
    workflow.set_entry_point("main_supervisor")

    # Add conditional edges from supervisor to teams
    workflow.add_conditional_edges(
        "main_supervisor",
        route_to_team,
        {
            "security_ops_team": "security_ops_team",
            "threat_intel_team": "threat_intel_team",
            "governance_team": "governance_team",
            "__end__": END,
        }
    )

    # Add edges from teams back to END
    workflow.add_edge("security_ops_team", END)
    workflow.add_edge("threat_intel_team", END)
    workflow.add_edge("governance_team", END)

    return workflow.compile()

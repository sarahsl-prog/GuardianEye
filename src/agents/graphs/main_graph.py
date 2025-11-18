"""Main supervisor graph for routing requests to team supervisors."""

import time
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from src.core.state import GuardianEyeState
from src.core.llm_factory import LLMFactory
from src.agents.graphs.security_ops_graph import create_security_ops_graph
from src.agents.graphs.threat_intel_graph import create_threat_intel_graph
from src.agents.graphs.governance_graph import create_governance_graph


def route_to_team(state: GuardianEyeState) -> Literal["security_ops", "threat_intel", "governance", "end"]:
    """Route request to appropriate team based on content analysis.

    Args:
        state: Current workflow state

    Returns:
        Team name or "end" to finish
    """
    messages = state["messages"]
    if not messages:
        return "end"

    # Get the last message
    last_message = messages[-1]
    query = last_message.content.lower() if hasattr(last_message, 'content') else ""

    # Simple keyword-based routing (can be enhanced with LLM-based routing)
    if any(keyword in query for keyword in [
        "incident", "triage", "alert", "anomaly", "investigation", "vulnerability", "vuln"
    ]):
        return "security_ops"
    elif any(keyword in query for keyword in [
        "threat", "hunting", "hunt", "recon", "reconnaissance", "intelligence"
    ]):
        return "threat_intel"
    elif any(keyword in query for keyword in [
        "compliance", "audit", "policy", "standard", "framework", "knowledge", "question", "how", "what"
    ]):
        return "governance"
    else:
        # Default to governance for general questions
        return "governance"


async def main_supervisor_node(state: GuardianEyeState) -> GuardianEyeState:
    """Main supervisor node for initial routing.

    Args:
        state: Current workflow state

    Returns:
        Updated state with routing information
    """
    # Initialize start time if not set
    if "start_time" not in state or not state["start_time"]:
        state["start_time"] = time.time()

    # Initialize execution path
    if "execution_path" not in state or not state["execution_path"]:
        state["execution_path"] = ["main_supervisor"]
    else:
        state["execution_path"].append("main_supervisor")

    # Determine next action
    next_team = route_to_team(state)
    state["next_action"] = next_team
    state["current_team"] = next_team

    return state


def create_main_graph():
    """Create the main supervisor graph.

    Returns:
        Compiled LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(GuardianEyeState)

    # Add main supervisor node
    workflow.add_node("main_supervisor", main_supervisor_node)

    # Create team subgraphs
    security_ops_graph = create_security_ops_graph()
    threat_intel_graph = create_threat_intel_graph()
    governance_graph = create_governance_graph()

    # Add team graphs as nodes
    workflow.add_node("security_ops", security_ops_graph)
    workflow.add_node("threat_intel", threat_intel_graph)
    workflow.add_node("governance", governance_graph)

    # Set entry point
    workflow.set_entry_point("main_supervisor")

    # Add conditional routing from main supervisor to teams
    workflow.add_conditional_edges(
        "main_supervisor",
        route_to_team,
        {
            "security_ops": "security_ops",
            "threat_intel": "threat_intel",
            "governance": "governance",
            "end": END
        }
    )

    # All teams return to END
    workflow.add_edge("security_ops", END)
    workflow.add_edge("threat_intel", END)
    workflow.add_edge("governance", END)

    return workflow.compile()

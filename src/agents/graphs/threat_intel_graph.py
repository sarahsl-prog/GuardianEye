"""Threat Intelligence team supervisor graph."""

from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END

from src.core.state import GuardianEyeState
from src.core.llm_factory import LLMFactory
from src.agents.specialists.threat_hunting import ThreatHuntingAgent
from src.agents.specialists.recon_orchestrator import ReconOrchestratorAgent
from src.agents.base.base_agent import AgentInput


def route_threat_intel(state: GuardianEyeState) -> Literal["threat_hunting", "recon_orchestrator", "end"]:
    """Route to appropriate threat intelligence agent.

    Args:
        state: Current workflow state

    Returns:
        Agent name or "end"
    """
    messages = state["messages"]
    if not messages:
        return "end"

    last_message = messages[-1]
    query = last_message.content.lower() if hasattr(last_message, 'content') else ""

    # Route based on keywords
    if any(keyword in query for keyword in ["threat", "hunt", "hunting", "hypothesis", "detect"]):
        return "threat_hunting"
    elif any(keyword in query for keyword in ["recon", "reconnaissance", "gather", "intelligence"]):
        return "recon_orchestrator"
    else:
        # Default to threat hunting
        return "threat_hunting"


async def threat_hunting_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute threat hunting agent."""
    llm = LLMFactory.get_default_llm()
    agent = ThreatHuntingAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("threat_hunting")

    return state


async def recon_orchestrator_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute recon orchestrator agent."""
    llm = LLMFactory.get_default_llm()
    agent = ReconOrchestratorAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("recon_orchestrator")

    return state


def create_threat_intel_graph():
    """Create the Threat Intelligence team graph.

    Returns:
        Compiled threat intelligence workflow
    """
    workflow = StateGraph(GuardianEyeState)

    # Add agent nodes
    workflow.add_node("threat_hunting", threat_hunting_node)
    workflow.add_node("recon_orchestrator", recon_orchestrator_node)

    # Set entry point with conditional routing
    workflow.set_conditional_entry_point(
        route_threat_intel,
        {
            "threat_hunting": "threat_hunting",
            "recon_orchestrator": "recon_orchestrator",
            "end": END
        }
    )

    # All agents go to END
    workflow.add_edge("threat_hunting", END)
    workflow.add_edge("recon_orchestrator", END)

    return workflow.compile()

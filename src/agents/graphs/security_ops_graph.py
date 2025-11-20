"""Security Operations team supervisor graph."""

from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END

from src.core.state import GuardianEyeState
from src.core.llm_factory import LLMFactory
from src.agents.specialists.incident_triage import IncidentTriageAgent
from src.agents.specialists.anomaly_investigation import AnomalyInvestigationAgent
from src.agents.specialists.vulnerability_prioritization import VulnerabilityPrioritizationAgent
from src.agents.base.base_agent import AgentInput


def route_security_ops(state: GuardianEyeState) -> Literal["incident_triage", "anomaly_investigation", "vulnerability_prioritization", "end"]:
    """Route to appropriate security operations agent.

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
    if any(keyword in query for keyword in ["incident", "triage", "alert", "response"]):
        return "incident_triage"
    elif any(keyword in query for keyword in ["anomaly", "unusual", "abnormal", "investigation"]):
        return "anomaly_investigation"
    elif any(keyword in query for keyword in ["vulnerability", "vuln", "cve", "patch", "prioritize"]):
        return "vulnerability_prioritization"
    else:
        # Default to incident triage
        return "incident_triage"


async def incident_triage_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute incident triage agent."""
    llm = LLMFactory.get_default_llm()
    agent = IncidentTriageAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    # Add result to messages
    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("incident_triage")

    return state


async def anomaly_investigation_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute anomaly investigation agent."""
    llm = LLMFactory.get_default_llm()
    agent = AnomalyInvestigationAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("anomaly_investigation")

    return state


async def vulnerability_prioritization_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute vulnerability prioritization agent."""
    llm = LLMFactory.get_default_llm()
    agent = VulnerabilityPrioritizationAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("vulnerability_prioritization")

    return state


def create_security_ops_graph():
    """Create the Security Operations team graph.

    Returns:
        Compiled security operations workflow
    """
    workflow = StateGraph(GuardianEyeState)

    # Add agent nodes
    workflow.add_node("incident_triage", incident_triage_node)
    workflow.add_node("anomaly_investigation", anomaly_investigation_node)
    workflow.add_node("vulnerability_prioritization", vulnerability_prioritization_node)

    # Set entry point with conditional routing
    workflow.set_conditional_entry_point(
        route_security_ops,
        {
            "incident_triage": "incident_triage",
            "anomaly_investigation": "anomaly_investigation",
            "vulnerability_prioritization": "vulnerability_prioritization",
            "end": END
        }
    )

    # All agents go to END
    workflow.add_edge("incident_triage", END)
    workflow.add_edge("anomaly_investigation", END)
    workflow.add_edge("vulnerability_prioritization", END)

    return workflow.compile()

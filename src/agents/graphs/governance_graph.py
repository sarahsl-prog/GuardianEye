"""Governance team supervisor graph."""

from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END

from src.core.state import GuardianEyeState
from src.core.llm_factory import LLMFactory
from src.agents.specialists.compliance_auditor import ComplianceAuditorAgent
from src.agents.specialists.security_knowledge import SecurityKnowledgeAgent
from src.agents.base.base_agent import AgentInput


def route_governance(state: GuardianEyeState) -> Literal["compliance_auditor", "security_knowledge", "end"]:
    """Route to appropriate governance agent.

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
    if any(keyword in query for keyword in ["compliance", "audit", "framework", "standard", "regulation"]):
        return "compliance_auditor"
    else:
        # Default to security knowledge for questions
        return "security_knowledge"


async def compliance_auditor_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute compliance auditor agent."""
    llm = LLMFactory.get_default_llm()
    agent = ComplianceAuditorAgent(llm)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("compliance_auditor")

    return state


async def security_knowledge_node(state: GuardianEyeState) -> GuardianEyeState:
    """Execute security knowledge agent with RAG."""
    llm = LLMFactory.get_default_llm()

    # Try to get vector store from state context
    vector_store = state.get("intermediate_results", {}).get("vector_store")
    agent = SecurityKnowledgeAgent(llm, vector_store=vector_store)

    messages = state["messages"]
    query = messages[-1].content if messages else ""

    agent_input = AgentInput(query=query, context=state.get("intermediate_results", {}))
    result = await agent.process(agent_input)

    state["messages"].append(AIMessage(content=result.result))
    state["final_result"] = result.result
    state["execution_path"].append("security_knowledge")

    return state


def create_governance_graph():
    """Create the Governance team graph.

    Returns:
        Compiled governance workflow
    """
    workflow = StateGraph(GuardianEyeState)

    # Add agent nodes
    workflow.add_node("compliance_auditor", compliance_auditor_node)
    workflow.add_node("security_knowledge", security_knowledge_node)

    # Set entry point with conditional routing
    workflow.set_conditional_entry_point(
        route_governance,
        {
            "compliance_auditor": "compliance_auditor",
            "security_knowledge": "security_knowledge",
            "end": END
        }
    )

    # All agents go to END
    workflow.add_edge("compliance_auditor", END)
    workflow.add_edge("security_knowledge", END)

    return workflow.compile()

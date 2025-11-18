"""State definitions for LangGraph multi-agent system."""

from typing import Annotated, Sequence, TypedDict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class GuardianEyeState(TypedDict):
    """Shared state across all agents in the GuardianEye system.

    This state is passed between agents and supervisors in the LangGraph workflow.
    """

    # Conversation history
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User context
    user_id: str
    session_id: str

    # Routing information
    current_team: str | None
    current_agent: str | None
    next_action: str | None

    # Results and data
    intermediate_results: dict[str, Any]
    final_result: str | None

    # Metadata
    execution_path: list[str]
    tool_calls: list[dict[str, Any]]
    total_tokens: int
    start_time: float

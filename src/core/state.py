"""Shared state definitions for LangGraph agents."""

from typing import Annotated, Any, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GuardianEyeState(TypedDict):
    """Shared state across all agents in the GuardianEye system."""

    # Conversation history
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User context
    user_id: str
    session_id: str

    # Routing information
    current_team: str | None
    current_agent: str | None
    next_action: str | None

    # Results
    intermediate_results: dict[str, Any]
    final_result: str | None

    # Metadata
    execution_path: list[str]
    tool_calls: list[dict[str, Any]]
    total_tokens: int
    start_time: float

    # Error handling
    errors: list[str]

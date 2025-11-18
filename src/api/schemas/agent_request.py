"""Request schemas for agent endpoints."""

from typing import Any
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Base agent request."""

    query: str = Field(..., description="User query or task description")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the agent"
    )
    session_id: str | None = Field(
        default=None,
        description="Session ID for conversation continuity"
    )


class AgentExecuteRequest(AgentRequest):
    """Request for generic agent execution."""

    agent_name: str | None = Field(
        default=None,
        description="Specific agent to execute (optional)"
    )

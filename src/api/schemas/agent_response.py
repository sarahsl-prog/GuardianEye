"""Response schemas for agent endpoints."""

from typing import Any
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Agent execution response."""

    result: str = Field(..., description="Agent execution result")
    execution_path: list[str] = Field(
        default_factory=list,
        description="Path of agents executed"
    )
    session_id: str = Field(..., description="Session identifier")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata"
    )
    error: str | None = Field(
        default=None,
        description="Error message if execution failed"
    )

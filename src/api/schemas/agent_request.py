"""Agent request schemas."""

from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Standard request schema for agent execution."""

    query: str = Field(..., description="User query or input", min_length=1)
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the agent"
    )
    session_id: str | None = Field(
        None,
        description="Session ID for state persistence"
    )
    stream: bool = Field(
        False,
        description="Enable streaming responses"
    )
    agent_name: str | None = Field(
        None,
        description="Specific agent to use (optional, will auto-route if not provided)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "Analyze this security alert for priority and recommended actions",
                    "context": {
                        "alert_details": "Suspicious login from unknown IP",
                        "alert_severity": "high"
                    },
                    "session_id": "session_123",
                    "stream": False
                }
            ]
        }
    }

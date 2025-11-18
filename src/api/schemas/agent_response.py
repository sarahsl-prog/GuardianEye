"""Agent response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Standard response schema for agent execution."""

    result: str = Field(..., description="Main result from the agent")
    agent_name: str = Field(..., description="Name of the agent that processed the request")
    execution_time: float = Field(..., description="Execution time in seconds", ge=0)
    tokens_used: int | None = Field(None, description="Number of tokens used", ge=0)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the execution"
    )
    session_id: str | None = Field(None, description="Session ID if provided")
    execution_path: list[str] = Field(
        default_factory=list,
        description="Path of agents/supervisors involved"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": "This alert indicates a high-priority security incident...",
                    "agent_name": "incident_triage",
                    "execution_time": 2.34,
                    "tokens_used": 450,
                    "metadata": {
                        "severity": "high",
                        "confidence": 0.95
                    },
                    "session_id": "session_123",
                    "execution_path": [
                        "main_supervisor -> security_ops_team",
                        "security_ops_team -> incident_triage"
                    ]
                }
            ]
        }
    }

"""Abstract base class for all GuardianEye agents."""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel


class AgentInput(BaseModel):
    """Base input schema for all agents."""

    query: str = Field(..., description="User query or task description")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context data"
    )


class AgentOutput(BaseModel):
    """Base output schema for all agents."""

    result: str = Field(..., description="Agent execution result")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata"
    )
    next_agent: str | None = Field(
        default=None, description="Suggested next agent to execute"
    )


class BaseAgent(ABC):
    """Abstract base class for all GuardianEye agents."""

    def __init__(self, llm: BaseChatModel, name: str):
        """Initialize the agent.

        Args:
            llm: Language model instance
            name: Agent name identifier
        """
        self.llm = llm
        self.name = name

    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process input and return output.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent output with result and metadata
        """
        pass

    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent.

        Returns:
            Prompt template string
        """
        pass

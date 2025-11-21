"""Base agent interface for all specialist agents."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Base input schema for all agents."""

    query: str = Field(..., description="User query or input")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    session_id: str | None = Field(None, description="Session ID for state tracking")


class AgentOutput(BaseModel):
    """Base output schema for all agents."""

    result: str = Field(..., description="Main result from the agent")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    next_agent: str | None = Field(None, description="Next agent to call, if any")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")


class BaseAgent(ABC):
    """Abstract base class for all specialist agents."""

    def __init__(self, llm: BaseChatModel, name: str):
        """
        Initialize the agent.

        Args:
            llm: Language model to use for this agent
            name: Unique identifier for this agent
        """
        self.llm = llm
        self.name = name

    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process input and return output.

        Args:
            input_data: Input data for the agent

        Returns:
            AgentOutput with results
        """
        pass

    @abstractmethod
    def get_prompt_template(self) -> ChatPromptTemplate:
        """
        Return the prompt template for this agent.

        Returns:
            ChatPromptTemplate for agent prompts
        """
        pass

    def get_name(self) -> str:
        """Get the agent's name."""
        return self.name

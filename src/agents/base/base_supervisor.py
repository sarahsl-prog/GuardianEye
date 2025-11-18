"""Base supervisor interface for coordinating agents."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel


class BaseSupervisor(ABC):
    """Abstract base class for all supervisor agents."""

    def __init__(self, llm: BaseChatModel, name: str):
        """
        Initialize the supervisor.

        Args:
            llm: Language model to use for routing decisions
            name: Unique identifier for this supervisor
        """
        self.llm = llm
        self.name = name

    @abstractmethod
    async def route(self, state: dict[str, Any]) -> str:
        """
        Determine which agent or team should handle the request.

        Args:
            state: Current state of the conversation/workflow

        Returns:
            Name of the next agent/team to invoke
        """
        pass

    @abstractmethod
    def get_available_agents(self) -> list[str]:
        """
        Get list of agents this supervisor can route to.

        Returns:
            List of agent names
        """
        pass

    def get_name(self) -> str:
        """Get the supervisor's name."""
        return self.name

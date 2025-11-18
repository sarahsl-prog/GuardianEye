"""Main supervisor for routing requests to team supervisors."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_supervisor import BaseSupervisor
from src.config.agent_registry import TeamType
from src.core.prompts import MAIN_SUPERVISOR_SYSTEM_PROMPT


class MainSupervisor(BaseSupervisor):
    """Main supervisor that routes requests to appropriate team supervisors."""

    def __init__(self, llm: BaseChatModel):
        """Initialize main supervisor."""
        super().__init__(llm, name="main_supervisor")
        self.parser = StrOutputParser()

    async def route(self, state: dict[str, Any]) -> str:
        """
        Route request to appropriate team supervisor.

        Args:
            state: Current conversation state

        Returns:
            Name of team to route to
        """
        # Get the last message from the user
        messages = state.get("messages", [])
        if not messages:
            return "FINISH"

        last_message = messages[-1]

        # Create routing prompt
        routing_messages = [
            SystemMessage(content=MAIN_SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=f"User request: {last_message.content}")
        ]

        # Get routing decision from LLM
        response = await self.llm.ainvoke(routing_messages)
        team = self.parser.parse(response.content).strip().lower()

        # Validate team selection
        valid_teams = [t.value for t in TeamType] + ["finish"]
        if team not in valid_teams:
            # Default to security ops if unclear
            return TeamType.SECURITY_OPS.value

        return team if team != "finish" else "FINISH"

    def get_available_agents(self) -> list[str]:
        """Get list of available teams."""
        return [t.value for t in TeamType] + ["FINISH"]

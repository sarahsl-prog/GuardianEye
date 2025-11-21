"""Governance Team Supervisor."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_supervisor import BaseSupervisor
from src.config.agent_registry import AgentType, TEAM_AGENTS_MAPPING, TeamType
from src.core.prompts import GOVERNANCE_SUPERVISOR_PROMPT


class GovernanceSupervisor(BaseSupervisor):
    """Supervisor for governance team agents."""

    def __init__(self, llm: BaseChatModel):
        """Initialize governance supervisor."""
        super().__init__(llm, name="governance_supervisor")
        self.parser = StrOutputParser()

    async def route(self, state: dict[str, Any]) -> str:
        """
        Route request to appropriate governance agent.

        Args:
            state: Current conversation state

        Returns:
            Name of agent to route to
        """
        messages = state.get("messages", [])
        if not messages:
            return "FINISH"

        last_message = messages[-1]

        # Create routing prompt
        routing_messages = [
            SystemMessage(content=GOVERNANCE_SUPERVISOR_PROMPT),
            HumanMessage(content=f"Request: {last_message.content}")
        ]

        # Get routing decision
        response = await self.llm.ainvoke(routing_messages)
        agent = self.parser.parse(response.content).strip().lower()

        # Validate agent selection
        valid_agents = [a.value for a in TEAM_AGENTS_MAPPING[TeamType.GOVERNANCE]]
        valid_agents.append("finish")

        if agent not in valid_agents:
            # Default to security knowledge
            return AgentType.SECURITY_KNOWLEDGE.value

        return agent if agent != "finish" else "FINISH"

    def get_available_agents(self) -> list[str]:
        """Get list of available agents in governance team."""
        agents = [a.value for a in TEAM_AGENTS_MAPPING[TeamType.GOVERNANCE]]
        return agents + ["FINISH"]

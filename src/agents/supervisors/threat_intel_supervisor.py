"""Threat Intelligence Team Supervisor."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_supervisor import BaseSupervisor
from src.config.agent_registry import AgentType, TEAM_AGENTS_MAPPING, TeamType
from src.core.prompts import THREAT_INTEL_SUPERVISOR_PROMPT


class ThreatIntelSupervisor(BaseSupervisor):
    """Supervisor for threat intelligence team agents."""

    def __init__(self, llm: BaseChatModel):
        """Initialize threat intel supervisor."""
        super().__init__(llm, name="threat_intel_supervisor")
        self.parser = StrOutputParser()

    async def route(self, state: dict[str, Any]) -> str:
        """
        Route request to appropriate threat intel agent.

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
            SystemMessage(content=THREAT_INTEL_SUPERVISOR_PROMPT),
            HumanMessage(content=f"Request: {last_message.content}")
        ]

        # Get routing decision
        response = await self.llm.ainvoke(routing_messages)
        agent = self.parser.parse(response.content).strip().lower()

        # Validate agent selection
        valid_agents = [a.value for a in TEAM_AGENTS_MAPPING[TeamType.THREAT_INTEL]]
        valid_agents.append("finish")

        if agent not in valid_agents:
            # Default to threat hunting
            return AgentType.THREAT_HUNTING.value

        return agent if agent != "finish" else "FINISH"

    def get_available_agents(self) -> list[str]:
        """Get list of available agents in threat intel team."""
        agents = [a.value for a in TEAM_AGENTS_MAPPING[TeamType.THREAT_INTEL]]
        return agents + ["FINISH"]

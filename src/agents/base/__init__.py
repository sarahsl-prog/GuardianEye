"""Base classes for all agents."""

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.agents.base.base_supervisor import BaseSupervisor

__all__ = ["BaseAgent", "BaseSupervisor", "AgentInput", "AgentOutput"]

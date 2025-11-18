"""Agent execution service."""

from typing import Any

from src.agents.base.base_agent import AgentInput
from src.config.agent_registry import AgentType
from src.core.llm_factory import LLMFactory


class AgentService:
    """Service for executing agents and managing agent lifecycle."""

    def __init__(self):
        """Initialize agent service."""
        self.llm = LLMFactory.get_default_llm()

    async def execute_agent(
        self,
        agent_name: str,
        query: str,
        context: dict[str, Any] | None = None,
        session_id: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a specific agent.

        Args:
            agent_name: Name of the agent to execute
            query: User query
            context: Additional context
            session_id: Session ID for state persistence

        Returns:
            Dictionary with execution results

        Raises:
            ValueError: If agent_name is invalid
        """
        # Validate agent name
        try:
            agent_type = AgentType(agent_name)
        except ValueError:
            raise ValueError(f"Invalid agent name: {agent_name}")

        # Create agent input
        agent_input = AgentInput(
            query=query,
            context=context or {},
            session_id=session_id
        )

        # Get appropriate agent instance
        agent = self._get_agent_instance(agent_type)

        # Execute agent
        result = await agent.process(agent_input)

        return {
            "result": result.result,
            "metadata": result.metadata,
            "agent_name": agent_name,
        }

    def _get_agent_instance(self, agent_type: AgentType):
        """
        Get agent instance based on agent type.

        Args:
            agent_type: Type of agent to instantiate

        Returns:
            Agent instance

        Raises:
            ValueError: If agent type not implemented
        """
        from src.agents.specialists.anomaly_investigation import (
            AnomalyInvestigationAgent,
        )
        from src.agents.specialists.compliance_auditor import ComplianceAuditorAgent
        from src.agents.specialists.incident_triage import IncidentTriageAgent
        from src.agents.specialists.recon_orchestrator import ReconOrchestratorAgent
        from src.agents.specialists.security_knowledge import SecurityKnowledgeAgent
        from src.agents.specialists.threat_hunting import ThreatHuntingAgent
        from src.agents.specialists.vulnerability_prioritization import (
            VulnerabilityPrioritizationAgent,
        )

        agent_map = {
            AgentType.INCIDENT_TRIAGE: IncidentTriageAgent,
            AgentType.ANOMALY_INVESTIGATION: AnomalyInvestigationAgent,
            AgentType.VULNERABILITY_PRIORITIZATION: VulnerabilityPrioritizationAgent,
            AgentType.THREAT_HUNTING: ThreatHuntingAgent,
            AgentType.RECON_ORCHESTRATOR: ReconOrchestratorAgent,
            AgentType.COMPLIANCE_AUDITOR: ComplianceAuditorAgent,
            AgentType.SECURITY_KNOWLEDGE: SecurityKnowledgeAgent,
        }

        agent_class = agent_map.get(agent_type)
        if not agent_class:
            raise ValueError(f"Agent not implemented: {agent_type}")

        return agent_class(self.llm)

"""Central registry for all agents in the system."""

from enum import Enum


class AgentType(str, Enum):
    """Available agent types."""

    # Supervisors
    MAIN_SUPERVISOR = "main_supervisor"
    SECURITY_OPS_SUPERVISOR = "security_ops_supervisor"
    THREAT_INTEL_SUPERVISOR = "threat_intel_supervisor"
    GOVERNANCE_SUPERVISOR = "governance_supervisor"

    # Specialist Agents - Security Operations
    INCIDENT_TRIAGE = "incident_triage"
    ANOMALY_INVESTIGATION = "anomaly_investigation"
    VULNERABILITY_PRIORITIZATION = "vulnerability_prioritization"

    # Specialist Agents - Threat Intelligence
    THREAT_HUNTING = "threat_hunting"
    RECON_ORCHESTRATOR = "recon_orchestrator"

    # Specialist Agents - Governance
    COMPLIANCE_AUDITOR = "compliance_auditor"
    SECURITY_KNOWLEDGE = "security_knowledge"


class TeamType(str, Enum):
    """Available team types."""

    SECURITY_OPS = "security_ops_team"
    THREAT_INTEL = "threat_intel_team"
    GOVERNANCE = "governance_team"


# Agent to Team mapping
AGENT_TEAM_MAPPING = {
    AgentType.INCIDENT_TRIAGE: TeamType.SECURITY_OPS,
    AgentType.ANOMALY_INVESTIGATION: TeamType.SECURITY_OPS,
    AgentType.VULNERABILITY_PRIORITIZATION: TeamType.SECURITY_OPS,
    AgentType.THREAT_HUNTING: TeamType.THREAT_INTEL,
    AgentType.RECON_ORCHESTRATOR: TeamType.THREAT_INTEL,
    AgentType.COMPLIANCE_AUDITOR: TeamType.GOVERNANCE,
    AgentType.SECURITY_KNOWLEDGE: TeamType.GOVERNANCE,
}

# Team to Agents mapping
TEAM_AGENTS_MAPPING = {
    TeamType.SECURITY_OPS: [
        AgentType.INCIDENT_TRIAGE,
        AgentType.ANOMALY_INVESTIGATION,
        AgentType.VULNERABILITY_PRIORITIZATION,
    ],
    TeamType.THREAT_INTEL: [
        AgentType.THREAT_HUNTING,
        AgentType.RECON_ORCHESTRATOR,
    ],
    TeamType.GOVERNANCE: [
        AgentType.COMPLIANCE_AUDITOR,
        AgentType.SECURITY_KNOWLEDGE,
    ],
}

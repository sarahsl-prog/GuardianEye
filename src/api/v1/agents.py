"""Agent execution endpoints."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_current_user_optional
from src.api.schemas.agent_request import AgentRequest
from src.api.schemas.agent_response import AgentResponse
from src.agents.specialists.anomaly_investigation import AnomalyInvestigationAgent
from src.agents.specialists.compliance_auditor import ComplianceAuditorAgent
from src.agents.specialists.incident_triage import IncidentTriageAgent
from src.agents.specialists.recon_orchestrator import ReconOrchestratorAgent
from src.agents.specialists.security_knowledge import SecurityKnowledgeAgent
from src.agents.specialists.threat_hunting import ThreatHuntingAgent
from src.agents.specialists.vulnerability_prioritization import (
    VulnerabilityPrioritizationAgent,
)
from src.core.llm_factory import LLMFactory

router = APIRouter()


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    user: Annotated[dict | None, Depends(get_current_user_optional)] = None
):
    """
    Execute an agent based on the request.

    This endpoint routes requests through the multi-agent orchestration system,
    which intelligently routes to the appropriate team and specialist agent.

    Args:
        request: Agent execution request
        user: Optional authenticated user

    Returns:
        AgentResponse with results from the orchestrated multi-agent system
    """
    try:
        # Use AgentService for full graph-based orchestration
        from src.services.agent_service import AgentService

        service = AgentService()

        # Extract user ID from auth context
        user_id = user.get("user_id", "anonymous") if user else "anonymous"

        # Execute query through the multi-agent system
        result = await service.execute_query(
            query=request.query,
            user_id=user_id,
            session_id=request.session_id,
            context=request.context
        )

        # Map service response to AgentResponse schema
        return AgentResponse(
            result=result["result"],
            agent_name=result["metadata"].get("agent", "multi-agent-system"),
            execution_time=result["execution_time"],
            metadata=result["metadata"],
            session_id=result["session_id"],
            execution_path=result["execution_path"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident-triage", response_model=AgentResponse)
async def run_incident_triage(
    request: AgentRequest,
    user: Annotated[dict | None, Depends(get_current_user_optional)] = None
):
    """Execute incident triage agent."""
    start_time = time.time()

    try:
        llm = LLMFactory.get_default_llm()
        agent = IncidentTriageAgent(llm)

        from src.agents.base.base_agent import AgentInput
        agent_input = AgentInput(
            query=request.query,
            context=request.context,
            session_id=request.session_id
        )

        result = await agent.process(agent_input)
        execution_time = time.time() - start_time

        return AgentResponse(
            result=result.result,
            agent_name=agent.name,
            execution_time=execution_time,
            metadata=result.metadata,
            session_id=request.session_id,
            execution_path=[agent.name]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threat-hunting", response_model=AgentResponse)
async def run_threat_hunting(
    request: AgentRequest,
    user: Annotated[dict | None, Depends(get_current_user_optional)] = None
):
    """Execute threat hunting agent."""
    start_time = time.time()

    try:
        llm = LLMFactory.get_default_llm()
        agent = ThreatHuntingAgent(llm)

        from src.agents.base.base_agent import AgentInput
        agent_input = AgentInput(
            query=request.query,
            context=request.context,
            session_id=request.session_id
        )

        result = await agent.process(agent_input)
        execution_time = time.time() - start_time

        return AgentResponse(
            result=result.result,
            agent_name=agent.name,
            execution_time=execution_time,
            metadata=result.metadata,
            session_id=request.session_id,
            execution_path=[agent.name]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security-knowledge", response_model=AgentResponse)
async def run_security_knowledge(
    request: AgentRequest,
    user: Annotated[dict | None, Depends(get_current_user_optional)] = None
):
    """Execute security knowledge agent."""
    start_time = time.time()

    try:
        llm = LLMFactory.get_default_llm()
        agent = SecurityKnowledgeAgent(llm)

        from src.agents.base.base_agent import AgentInput
        agent_input = AgentInput(
            query=request.query,
            context=request.context,
            session_id=request.session_id
        )

        result = await agent.process(agent_input)
        execution_time = time.time() - start_time

        return AgentResponse(
            result=result.result,
            agent_name=agent.name,
            execution_time=execution_time,
            metadata=result.metadata,
            session_id=request.session_id,
            execution_path=[agent.name]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_agents():
    """
    List all available agents.

    Returns:
        Dictionary of available agents organized by team
    """
    return {
        "security_ops_team": [
            "incident_triage",
            "anomaly_investigation",
            "vulnerability_prioritization"
        ],
        "threat_intel_team": [
            "threat_hunting",
            "recon_orchestrator"
        ],
        "governance_team": [
            "compliance_auditor",
            "security_knowledge"
        ]
    }

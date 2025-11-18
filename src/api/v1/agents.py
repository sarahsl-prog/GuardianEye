"""Agent execution endpoints."""

from fastapi import APIRouter, Depends

from src.api.schemas.agent_request import AgentRequest, AgentExecuteRequest
from src.api.schemas.agent_response import AgentResponse
from src.api.deps import get_current_user_optional
from src.services.agent_service import AgentService


router = APIRouter()


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentExecuteRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute multi-agent workflow.

    This endpoint automatically routes the query to the appropriate
    team and agent based on content analysis.

    Args:
        request: Agent execution request
        current_user: Optional authenticated user

    Returns:
        Agent execution result
    """
    service = AgentService()

    # Get user ID from token or use default
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    result = await service.execute_query(
        query=request.query,
        user_id=user_id,
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(**result)


@router.post("/incident-triage", response_model=AgentResponse)
async def incident_triage(
    request: AgentRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute incident triage agent.

    Args:
        request: Incident details
        current_user: Optional authenticated user

    Returns:
        Triage analysis and recommendations
    """
    service = AgentService()
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    # Add routing hint to ensure incident triage agent is used
    context = request.context.copy()
    context["force_route"] = "incident_triage"

    result = await service.execute_query(
        query=f"incident triage: {request.query}",
        user_id=user_id,
        session_id=request.session_id,
        context=context
    )

    return AgentResponse(**result)


@router.post("/threat-hunting", response_model=AgentResponse)
async def threat_hunting(
    request: AgentRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute threat hunting agent.

    Args:
        request: Threat hunting request
        current_user: Optional authenticated user

    Returns:
        Threat hunting analysis and hypotheses
    """
    service = AgentService()
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    result = await service.execute_query(
        query=f"threat hunting: {request.query}",
        user_id=user_id,
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(**result)


@router.post("/anomaly-investigation", response_model=AgentResponse)
async def anomaly_investigation(
    request: AgentRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute anomaly investigation agent.

    Args:
        request: Anomaly investigation request
        current_user: Optional authenticated user

    Returns:
        Anomaly analysis
    """
    service = AgentService()
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    result = await service.execute_query(
        query=f"anomaly investigation: {request.query}",
        user_id=user_id,
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(**result)


@router.post("/compliance-audit", response_model=AgentResponse)
async def compliance_audit(
    request: AgentRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute compliance auditor agent.

    Args:
        request: Compliance audit request
        current_user: Optional authenticated user

    Returns:
        Compliance audit summary
    """
    service = AgentService()
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    result = await service.execute_query(
        query=f"compliance audit: {request.query}",
        user_id=user_id,
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(**result)


@router.post("/security-knowledge", response_model=AgentResponse)
async def security_knowledge(
    request: AgentRequest,
    current_user: dict | None = Depends(get_current_user_optional)
):
    """Execute security knowledge agent with RAG.

    Args:
        request: Security question
        current_user: Optional authenticated user

    Returns:
        Answer with security knowledge
    """
    service = AgentService()
    user_id = current_user.get("username", "anonymous") if current_user else "anonymous"

    result = await service.execute_query(
        query=request.query,
        user_id=user_id,
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(**result)

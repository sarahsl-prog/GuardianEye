"""Health check endpoints."""

from fastapi import APIRouter

from src.api.schemas.common import HealthResponse
from src.config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is operational.

    Returns:
        HealthResponse with status and configuration info
    """
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        environment=settings.app_env,
        llm_provider=settings.llm_provider
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.

    Returns:
        Simple ready status
    """
    # TODO: Add checks for database connectivity, LLM availability, etc.
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.

    Returns:
        Simple alive status
    """
    return {"alive": True}

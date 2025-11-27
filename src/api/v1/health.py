"""Health check endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from src.api.schemas.common import HealthResponse
from src.config.settings import settings
from src.db.postgres import get_postgres_connection
from src.db.redis import get_redis_client
from src.core.llm_factory import LLMFactory

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

    Checks:
    - PostgreSQL database connectivity
    - Redis cache connectivity
    - LLM provider availability

    Returns:
        Ready status with details of each service

    Raises:
        HTTPException: If any service is unavailable
    """
    checks = {
        "ready": True,
        "services": {
            "postgres": "unknown",
            "redis": "unknown",
            "llm": "unknown"
        }
    }

    # Check PostgreSQL
    try:
        engine = get_postgres_connection()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["services"]["postgres"] = "healthy"
    except Exception as e:
        checks["services"]["postgres"] = f"unhealthy: {str(e)}"
        checks["ready"] = False

    # Check Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        checks["services"]["redis"] = "healthy"
    except Exception as e:
        checks["services"]["redis"] = f"unhealthy: {str(e)}"
        checks["ready"] = False

    # Check LLM availability
    try:
        llm = LLMFactory.get_default_llm()
        # For local providers (Ollama, LMStudio), we can't easily verify without making a call
        # For cloud providers, the factory will raise an error if API keys are missing
        checks["services"]["llm"] = "healthy"
    except Exception as e:
        checks["services"]["llm"] = f"unhealthy: {str(e)}"
        checks["ready"] = False

    if not checks["ready"]:
        raise HTTPException(status_code=503, detail=checks)

    return checks


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.

    Returns:
        Simple alive status
    """
    return {"alive": True}

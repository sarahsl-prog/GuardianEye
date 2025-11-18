"""Health check endpoints."""

from fastapi import APIRouter

from src.config.settings import settings


router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "2.0.0",
        "environment": settings.app_env
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint.

    Returns:
        Service readiness status
    """
    # Can add checks for database, Redis, vector store, etc.
    return {
        "status": "ready",
        "service": settings.app_name
    }

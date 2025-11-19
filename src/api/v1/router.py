"""Main API router."""

from fastapi import APIRouter

from .agents import router as agents_router
from .auth import router as auth_router
from .health import router as health_router


api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])

"""Main API router combining all v1 endpoints."""

from fastapi import APIRouter

from src.api.v1 import agents, health

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

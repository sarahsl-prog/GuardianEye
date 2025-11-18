"""FastAPI application entry point for GuardianEye."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import logging_middleware
from src.api.v1.router import api_router
from src.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("GuardianEye starting up...")
    print(f"Environment: {settings.app_env}")
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Model: {settings.llm_model}")

    yield

    # Shutdown
    print("GuardianEye shutting down...")


app = FastAPI(
    title="GuardianEye API",
    description="AI-Powered Security Operations Center Dashboard",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(logging_middleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GuardianEye API",
        "version": "2.0.0",
        "description": "AI-Powered Security Operations Center",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.app_env,
        "llm_provider": settings.llm_provider
    }

"""FastAPI application entry point."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.api.v1.router import api_router
from src.db.vector_store import initialize_vector_store, seed_security_knowledge
from src.db.redis import close_redis_client
from src.db.postgres import close_postgres_connection


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting GuardianEye application", env=settings.app_env)

    # Initialize vector store
    try:
        initialize_vector_store()
        logger.info("Vector store initialized")

        # Seed with security knowledge (only in development)
        if settings.app_env == "development":
            seed_security_knowledge()
            logger.info("Vector store seeded with security knowledge")
    except Exception as e:
        logger.warning("Failed to initialize vector store", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down GuardianEye application")
    await close_redis_client()
    await close_postgres_connection()


# Create FastAPI application
app = FastAPI(
    title="GuardianEye API",
    description="AI-Powered Security Operations Center with Multi-Agent Orchestration",
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


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to GuardianEye API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower()
    )

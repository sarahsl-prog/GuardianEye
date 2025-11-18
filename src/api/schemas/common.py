"""Common schemas used across the API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str | None = Field(None, description="Environment")
    llm_provider: str | None = Field(None, description="LLM provider")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    code: str | None = Field(None, description="Error code")

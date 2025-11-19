"""Authentication request/response schemas."""

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Token generation request."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token generation response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

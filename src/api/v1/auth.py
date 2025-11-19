"""Authentication endpoints."""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status

from src.api.schemas.auth import TokenRequest, TokenResponse
from src.services.auth_service import create_access_token
from src.config.settings import settings


router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """Generate JWT access token.

    Args:
        request: Login credentials

    Returns:
        JWT access token

    Note:
        This is a simplified implementation. In production, validate
        against a user database.
    """
    # Simplified authentication - in production, validate against database
    # For demo purposes, accept any username/password
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": request.username, "username": request.username},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh")
async def refresh_token():
    """Refresh access token.

    Returns:
        New JWT access token
    """
    # Implement token refresh logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )

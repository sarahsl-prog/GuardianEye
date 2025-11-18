"""Dependency injection for FastAPI routes."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None
):
    """
    Verify JWT token and return current user.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User information (placeholder for now)

    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement actual JWT verification
    # For now, this is a placeholder that allows unauthenticated access
    if credentials is None:
        # Allow anonymous access for development
        return {"user_id": "anonymous", "username": "anonymous"}

    # Placeholder token verification
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return placeholder user
    return {
        "user_id": "user_123",
        "username": "demo_user",
        "email": "demo@guardianeye.ai"
    }


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None
):
    """
    Get current user if authenticated, None otherwise.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User information or None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

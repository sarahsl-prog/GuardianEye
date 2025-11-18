"""FastAPI dependencies for dependency injection."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.auth_service import verify_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return current user.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User information from token

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = await verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    )
) -> dict | None:
    """Optionally verify JWT token.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        User information if token provided and valid, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return await verify_token(token)

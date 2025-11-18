"""Authentication endpoints (placeholder)."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    """Login endpoint (placeholder)."""
    # TODO: Implement actual authentication
    return {"message": "Authentication not yet implemented"}


@router.post("/logout")
async def logout():
    """Logout endpoint (placeholder)."""
    # TODO: Implement actual logout
    return {"message": "Logout not yet implemented"}

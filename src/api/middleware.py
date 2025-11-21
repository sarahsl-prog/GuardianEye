"""Custom middleware for FastAPI."""

import time
from typing import Callable

from fastapi import Request, Response


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log request and response information.

    Args:
        request: FastAPI request
        call_next: Next middleware/route handler

    Returns:
        Response from the next handler
    """
    start_time = time.time()

    # Log request
    print(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    print(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")

    return response

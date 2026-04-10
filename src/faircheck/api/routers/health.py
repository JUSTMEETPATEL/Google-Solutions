"""Health check endpoint.

Provides a lightweight liveness probe that returns within 100ms.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok"}

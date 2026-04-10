"""Oversight / governance endpoint.

Provides governance metadata and compliance tracking.
Stub — full implementation deferred until the governance phase.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/oversight", tags=["oversight"])


@router.post("/")
async def oversight_action() -> dict:
    """Perform a governance / oversight action.

    Stub — will be implemented in the governance phase.
    """
    return {"status": "oversight_pending", "message": "Not yet implemented."}

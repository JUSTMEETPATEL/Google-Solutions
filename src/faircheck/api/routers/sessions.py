"""Session management endpoints.

Provides access to past scan results.  Full persistence is deferred to
Phase 5 (SQLite via SQLAlchemy); these stubs define the contract now.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/")
async def list_sessions() -> dict:
    """Return a list of past scan sessions.

    Stub — will be backed by SQLite in Phase 5.
    """
    return {"sessions": []}


@router.get("/{session_id}")
async def get_session(session_id: str) -> dict:
    """Return full detail for a single scan session.

    Stub — will be backed by SQLite in Phase 5.
    """
    raise HTTPException(
        status_code=404,
        detail=f"Session '{session_id}' not found.",
    )

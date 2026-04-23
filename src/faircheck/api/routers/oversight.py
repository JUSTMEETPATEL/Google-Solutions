"""Oversight / governance endpoint — manages human oversight records.

Records reviewer decisions, dates, and notes for compliance audit trails.
EU AI Act Article 14 requires documented human oversight.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oversight", tags=["oversight"])


class OversightRequest(BaseModel):
    """Request body for submitting an oversight decision."""
    session_id: str
    reviewer: str
    date: str | None = None
    decision: str  # "approved" | "rejected" | "conditional"
    notes: str | None = None


def _get_db():
    """Lazy-import DB to avoid circular imports."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.post("/")
async def submit_oversight(request: OversightRequest) -> dict:
    """Record a human oversight decision for a scan session.

    This fulfils EU AI Act Article 14 requirements for documented
    human oversight of AI system decisions.
    """
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        row = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{request.session_id}' not found.",
            )

        # Store the oversight decision
        oversight_data = {
            "reviewer": request.reviewer,
            "date": request.date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "decision": request.decision,
            "notes": request.notes or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        row.oversight_decision = request.decision

        # Also store in bias_metrics for report access
        bias_metrics = row.bias_metrics or {}
        bias_metrics["oversight"] = oversight_data
        row.bias_metrics = bias_metrics

        db.commit()

        return {
            "success": True,
            "session_id": request.session_id,
            "oversight": oversight_data,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Oversight submission failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.get("/{session_id}")
async def get_oversight(session_id: str) -> dict:
    """Retrieve the oversight decision for a session."""
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        row = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found.",
            )

        bias_metrics = row.bias_metrics or {}
        oversight = bias_metrics.get("oversight")

        return {
            "session_id": session_id,
            "has_oversight": oversight is not None,
            "oversight": oversight,
        }
    finally:
        db.close()

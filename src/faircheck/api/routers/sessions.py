"""Session management endpoints — backed by SQLite.

Provides full CRUD for past scan sessions including retrieval of
analysis results, explanations, intersectional analysis,
confidence intervals, feature attribution, and recommendations.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_db():
    """Lazy-import DB to avoid circular imports at module load."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.get("/")
async def list_sessions() -> dict:
    """Return a list of past scan sessions."""
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()
    try:
        rows = db.query(SessionModel).order_by(SessionModel.created_at.desc()).all()
        sessions = []
        for row in rows:
            sessions.append({
                "id": row.id,
                "model_name": row.model_path,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "risk_level": row.risk_level or "unknown",
                "status": row.status or "complete",
            })
        return {"sessions": sessions}
    finally:
        db.close()


@router.get("/{session_id}")
async def get_session(session_id: str) -> dict:
    """Return full detail for a single scan session."""
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()
    try:
        row = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found.",
            )

        # Unpack stored bias_metrics JSON
        bias_metrics = row.bias_metrics or {}
        return {
            "id": row.id,
            "session_id": row.id,
            "model_name": row.model_path,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "risk_level": row.risk_level or "unknown",
            "status": row.status or "complete",
            "analysis_results": bias_metrics.get("analysis_results", {}),
            "explanations": bias_metrics.get("explanations", {}),
            "intersectional_analysis": bias_metrics.get("intersectional_analysis"),
            "confidence_intervals": bias_metrics.get("confidence_intervals"),
            "feature_attribution": bias_metrics.get("feature_attribution"),
            "recommendations": bias_metrics.get("recommendations", []),
            "mitigation_history": row.mitigation_history,
            "oversight_decision": row.oversight_decision,
        }
    finally:
        db.close()


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a scan session."""
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()
    try:
        row = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found.",
            )
        db.delete(row)
        db.commit()
        return {"status": "deleted", "session_id": session_id}
    finally:
        db.close()

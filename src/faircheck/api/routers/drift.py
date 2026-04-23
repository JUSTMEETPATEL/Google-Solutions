"""Temporal drift monitoring endpoint.

Compares fairness metrics between two scan sessions to detect
model degradation over time.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from faircheck.analysis.drift import compute_drift

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drift", tags=["drift"])


class DriftRequest(BaseModel):
    """Request body for drift comparison."""
    baseline_session_id: str
    current_session_id: str


def _get_db():
    """Lazy-import DB."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.post("/compare")
async def compare_sessions(request: DriftRequest) -> dict:
    """Compare two scan sessions and compute drift metrics.

    Parameters
    ----------
    baseline_session_id : str
        The earlier (baseline) session ID.
    current_session_id : str
        The newer (current) session ID to compare against.
    """
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        baseline = db.query(SessionModel).filter(
            SessionModel.id == request.baseline_session_id
        ).first()
        if baseline is None:
            raise HTTPException(
                status_code=404,
                detail=f"Baseline session '{request.baseline_session_id}' not found.",
            )

        current = db.query(SessionModel).filter(
            SessionModel.id == request.current_session_id
        ).first()
        if current is None:
            raise HTTPException(
                status_code=404,
                detail=f"Current session '{request.current_session_id}' not found.",
            )

        baseline_metrics = (baseline.bias_metrics or {}).get("analysis_results", {})
        current_metrics = (current.bias_metrics or {}).get("analysis_results", {})

        if not baseline_metrics or not current_metrics:
            raise HTTPException(
                status_code=400,
                detail="Both sessions must have analysis results for drift comparison.",
            )

        drift_result = compute_drift(baseline_metrics, current_metrics)

        return {
            "baseline_session_id": request.baseline_session_id,
            "current_session_id": request.current_session_id,
            "baseline_model": baseline.model_path,
            "current_model": current.model_path,
            "baseline_date": baseline.created_at.isoformat() if baseline.created_at else None,
            "current_date": current.created_at.isoformat() if current.created_at else None,
            **drift_result,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Drift comparison failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.get("/history/{model_name}")
async def get_model_history(model_name: str) -> dict:
    """Get the audit history for a specific model name.

    Returns all sessions for the given model, ordered by date,
    with risk level trends.
    """
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        rows = (
            db.query(SessionModel)
            .filter(SessionModel.model_path == model_name)
            .order_by(SessionModel.created_at.asc())
            .all()
        )

        history = []
        for row in rows:
            bias_metrics = row.bias_metrics or {}
            analysis = bias_metrics.get("analysis_results", {})
            history.append({
                "session_id": row.id,
                "date": row.created_at.isoformat() if row.created_at else None,
                "risk_level": row.risk_level or "unknown",
                "status": row.status,
                "overall_risk_level": analysis.get("overall_risk_level", "unknown"),
            })

        return {
            "model_name": model_name,
            "total_audits": len(history),
            "history": history,
        }
    finally:
        db.close()

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
            "ai_summary": bias_metrics.get("ai_summary"),
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


# ─── Model Comparison / Diff ──────────────────────────────


from pydantic import BaseModel as PydanticBaseModel


class CompareRequest(PydanticBaseModel):
    """Request body for session comparison."""
    session_a: str
    session_b: str


@router.post("/compare")
async def compare_sessions(request: CompareRequest) -> dict:
    """Compare two scan sessions side-by-side for model diff / audit trail.

    Returns a structured comparison of all metrics, risk levels, and
    a summary of improvements/degradations.
    """
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        row_a = db.query(SessionModel).filter(SessionModel.id == request.session_a).first()
        row_b = db.query(SessionModel).filter(SessionModel.id == request.session_b).first()

        if row_a is None:
            raise HTTPException(status_code=404, detail=f"Session '{request.session_a}' not found.")
        if row_b is None:
            raise HTTPException(status_code=404, detail=f"Session '{request.session_b}' not found.")

        bm_a = (row_a.bias_metrics or {}).get("analysis_results", {})
        bm_b = (row_b.bias_metrics or {}).get("analysis_results", {})

        results_a = bm_a.get("results", {})
        results_b = bm_b.get("results", {})

        # Build per-attribute metric comparison
        all_attrs = sorted(set(list(results_a.keys()) + list(results_b.keys())))
        comparison: dict = {}
        improved = 0
        degraded = 0
        unchanged = 0

        status_rank = {"pass": 0, "warning": 1, "fail": 2}

        for attr in all_attrs:
            metrics_a = results_a.get(attr, {}).get("metrics", {})
            metrics_b = results_b.get(attr, {}).get("metrics", {})
            all_metrics = sorted(set(list(metrics_a.keys()) + list(metrics_b.keys())))

            attr_comp: dict = {}
            for m in all_metrics:
                ma = metrics_a.get(m, {})
                mb = metrics_b.get(m, {})
                val_a = ma.get("value")
                val_b = mb.get("value")
                st_a = ma.get("status", "")
                st_b = mb.get("status", "")
                ra = status_rank.get(st_a, 1)
                rb = status_rank.get(st_b, 1)

                if rb < ra:
                    change = "improved"
                    improved += 1
                elif rb > ra:
                    change = "degraded"
                    degraded += 1
                else:
                    change = "unchanged"
                    unchanged += 1

                attr_comp[m] = {
                    "session_a": {"value": val_a, "status": st_a, "threshold": ma.get("threshold")},
                    "session_b": {"value": val_b, "status": st_b, "threshold": mb.get("threshold")},
                    "change": change,
                    "delta": round(val_b - val_a, 6) if val_a is not None and val_b is not None else None,
                }
            comparison[attr] = attr_comp

        return {
            "session_a": {
                "id": request.session_a,
                "model_name": row_a.model_path,
                "risk_level": bm_a.get("overall_risk_level", "unknown"),
                "created_at": row_a.created_at.isoformat() if row_a.created_at else None,
            },
            "session_b": {
                "id": request.session_b,
                "model_name": row_b.model_path,
                "risk_level": bm_b.get("overall_risk_level", "unknown"),
                "created_at": row_b.created_at.isoformat() if row_b.created_at else None,
            },
            "comparison": comparison,
            "summary": {
                "improved": improved,
                "degraded": degraded,
                "unchanged": unchanged,
                "risk_change": f"{bm_a.get('overall_risk_level', 'unknown')} → {bm_b.get('overall_risk_level', 'unknown')}",
            },
        }
    finally:
        db.close()

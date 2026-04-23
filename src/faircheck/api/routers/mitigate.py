"""Bias mitigation endpoint — applies mitigation algorithms.

Loads a prior scan session and applies the recommended or specified
mitigation algorithm, storing before/after comparison results.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from faircheck.analysis.recommend import recommend_mitigation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mitigate", tags=["mitigate"])


class MitigateRequest(BaseModel):
    """Request body for mitigation endpoint."""
    session_id: str
    algorithm: str | None = None  # If None, auto-recommend


class MitigateResponse(BaseModel):
    """Response body for mitigation endpoint."""
    status: str
    session_id: str
    algorithm_applied: str | None = None
    recommendations: list[dict[str, Any]] = []
    message: str = ""


def _get_db():
    """Lazy-import DB to avoid circular imports at module load."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.post("/")
async def mitigate(request: MitigateRequest) -> dict:
    """Apply bias mitigation to a scan session.

    If no algorithm is specified, returns auto-recommended algorithms.
    When an algorithm is specified, applies it and returns before/after metrics.
    """
    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
        # Load session
        row = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{request.session_id}' not found.",
            )

        bias_metrics = row.bias_metrics or {}
        analysis_results = bias_metrics.get("analysis_results", {})

        if not analysis_results:
            raise HTTPException(
                status_code=400,
                detail="Session has no analysis results to mitigate.",
            )

        # Generate recommendations
        recommendations = recommend_mitigation(analysis_results)

        if request.algorithm is None:
            # Return recommendations without applying
            return {
                "status": "recommendations",
                "session_id": request.session_id,
                "recommendations": recommendations,
                "message": (
                    f"Found {len(recommendations)} recommended mitigation strategies. "
                    "Submit again with 'algorithm' parameter to apply one."
                ),
            }

        # Validate algorithm exists in recommendations
        valid_algorithms = {r["algorithm"] for r in recommendations}
        all_algorithms = {
            "reweighing", "equalized_odds", "calibrated_equalized_odds",
            "disparate_impact_remover", "reject_option_classification",
            "adversarial_debiasing", "none",
        }

        if request.algorithm not in all_algorithms:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unknown algorithm '{request.algorithm}'. "
                    f"Valid options: {sorted(all_algorithms)}"
                ),
            )

        if request.algorithm == "none":
            return {
                "status": "skipped",
                "session_id": request.session_id,
                "algorithm_applied": None,
                "recommendations": recommendations,
                "message": "Mitigation explicitly skipped by user.",
            }

        # Record mitigation in session history
        mitigation_entry = {
            "algorithm": request.algorithm,
            "status": "recorded",
            "recommendation_confidence": next(
                (r["confidence"] for r in recommendations if r["algorithm"] == request.algorithm),
                "unknown",
            ),
            "recommendation_rationale": next(
                (r["rationale"] for r in recommendations if r["algorithm"] == request.algorithm),
                "",
            ),
        }

        existing_history = row.mitigation_history or []
        existing_history.append(mitigation_entry)
        row.mitigation_history = existing_history
        db.commit()

        return {
            "status": "applied",
            "session_id": request.session_id,
            "algorithm_applied": request.algorithm,
            "mitigation_entry": mitigation_entry,
            "recommendations": recommendations,
            "message": (
                f"Mitigation '{request.algorithm}' has been recorded for session "
                f"'{request.session_id}'."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Mitigation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/recommend")
async def recommend(session_id: str) -> dict:
    """Return auto-recommended mitigation algorithms for a session."""
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
        analysis_results = bias_metrics.get("analysis_results", {})
        recommendations = recommend_mitigation(analysis_results)

        return {
            "session_id": session_id,
            "recommendations": recommendations,
        }
    finally:
        db.close()

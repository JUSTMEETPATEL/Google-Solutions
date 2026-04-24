"""Bias mitigation endpoint — actually applies mitigation algorithms.

Loads cached scan artifacts, runs the MitigationPipeline with real data,
and stores before/after comparison results in the session.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sklearn.model_selection import train_test_split

from faircheck.analysis.recommend import recommend_mitigation
from faircheck.api.cache import load_cached_artifacts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mitigate", tags=["mitigate"])


class MitigateRequest(BaseModel):
    """Request body for mitigation endpoint."""
    session_id: str
    algorithm: str | None = None  # If None, auto-recommend


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
    When an algorithm is specified, actually executes the mitigation
    pipeline and returns before/after metrics comparison.
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

        # Validate algorithm
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

        # --- Actually execute mitigation ---
        cached = load_cached_artifacts(request.session_id)
        if cached is None:
            # Fallback: record-only mode (no cached data)
            return _record_only_mitigation(
                db, row, request, recommendations
            )

        try:
            mitigation_result = _execute_mitigation(
                cached=cached,
                algorithm=request.algorithm,
                recommendations=recommendations,
            )
        except Exception as e:
            logger.exception("Mitigation execution failed: %s", e)
            # Fallback to record-only
            return _record_only_mitigation(
                db, row, request, recommendations,
                error_msg=str(e),
            )

        # Store mitigation result in session
        mitigation_entry = {
            "algorithm": request.algorithm,
            "status": "executed",
            "success": mitigation_result.get("success", False),
            "before_metrics": mitigation_result.get("before_metrics"),
            "after_metrics": mitigation_result.get("after_metrics"),
            "improvement_summary": mitigation_result.get("improvement_summary"),
            "recommendation_confidence": next(
                (r["confidence"] for r in recommendations if r["algorithm"] == request.algorithm),
                "unknown",
            ),
        }

        existing_history = row.mitigation_history or []
        existing_history.append(mitigation_entry)
        row.mitigation_history = existing_history

        # Also store latest mitigation in bias_metrics for report access
        bias_metrics["mitigation"] = mitigation_entry
        row.bias_metrics = bias_metrics

        db.commit()

        return {
            "status": "executed",
            "session_id": request.session_id,
            "algorithm_applied": request.algorithm,
            "mitigation_result": mitigation_entry,
            "recommendations": recommendations,
            "message": (
                f"Mitigation '{request.algorithm}' executed successfully. "
                f"See before/after comparison in mitigation_result."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Mitigation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()


def _execute_mitigation(
    cached: dict,
    algorithm: str,
    recommendations: list[dict],
) -> dict[str, Any]:
    """Load cached data, run mitigation pipeline, return before/after."""
    from faircheck.config import load_config
    from faircheck.ingestion.pipeline import IngestionPipeline
    from faircheck.mitigation.pipeline import MitigationPipeline

    config = load_config()

    # Load model + dataset from cache
    pipeline = IngestionPipeline()
    ingestion = pipeline.load(
        model_path=cached["model_path"],
        data_path=cached["dataset_path"],
    )

    # Build full dataframe
    chunks = list(ingestion.dataset.iter_chunks())
    df = pd.concat(chunks, ignore_index=True)

    feature_names = cached["feature_names"]
    protected_cols = cached["protected_cols"]
    target_col = cached["target_col"]

    X = df[feature_names]
    y = df[target_col].values

    # Train/test split for mitigation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Build sensitive features (train, test)
    sensitive_features = {}
    for col in protected_cols:
        if col in df.columns:
            train_idx = X_train.index
            test_idx = X_test.index
            sensitive_features[col] = (
                df[col].iloc[train_idx].reset_index(drop=True),
                df[col].iloc[test_idx].reset_index(drop=True),
            )

    if not sensitive_features:
        raise ValueError("No protected attributes found in cached data")

    # Get the raw model for mitigation
    raw_model = (
        ingestion.model._model
        if hasattr(ingestion.model, '_model')
        else ingestion.model
    )

    # Run mitigation pipeline
    mit_pipeline = MitigationPipeline(config=config)
    
    # Get original predictions from the raw model to compare against
    if hasattr(raw_model, "predict"):
        y_pred_before = raw_model.predict(X_test.reset_index(drop=True))
    else:
        y_pred_before = None
        
    result = mit_pipeline.run(
        algorithm=algorithm,
        X_train=X_train.reset_index(drop=True),
        y_train=y_train,
        X_test=X_test.reset_index(drop=True),
        y_test=y_test,
        sensitive_features=sensitive_features,
        y_pred_before=y_pred_before,
        estimator=raw_model,
    )

    # Extract before/after summary
    before_summary = _extract_metric_summary(result.before_metrics)
    after_summary = _extract_metric_summary(result.after_metrics) if result.after_metrics else None
    improvement = _compute_improvement(before_summary, after_summary) if after_summary else None

    return {
        "success": result.success,
        "before_metrics": before_summary,
        "after_metrics": after_summary,
        "improvement_summary": improvement,
        "error": getattr(result, "error", None),
    }


def _extract_metric_summary(analysis_dict: dict | None) -> dict[str, Any] | None:
    """Extract flat metric values from nested analysis results."""
    if not analysis_dict:
        return None

    results = analysis_dict.get("results", {})
    summary: dict[str, Any] = {
        "overall_risk_level": analysis_dict.get("overall_risk_level", "unknown"),
        "attributes": {},
    }

    for attr_name, attr_data in results.items():
        metrics = attr_data.get("metrics", {})
        attr_summary: dict[str, Any] = {}
        for m_name, m_data in metrics.items():
            attr_summary[m_name] = {
                "value": m_data.get("value"),
                "threshold": m_data.get("threshold"),
                "status": m_data.get("status"),
            }
        summary["attributes"][attr_name] = attr_summary

    return summary


def _compute_improvement(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Compute improvement summary between before and after metrics."""
    if not before or not after:
        return None

    improved = 0
    degraded = 0
    unchanged = 0
    details: list[dict[str, Any]] = []

    before_attrs = before.get("attributes", {})
    after_attrs = after.get("attributes", {})

    for attr_name in before_attrs:
        if attr_name not in after_attrs:
            continue
        for m_name in before_attrs[attr_name]:
            if m_name not in after_attrs[attr_name]:
                continue
            b_status = before_attrs[attr_name][m_name].get("status", "")
            a_status = after_attrs[attr_name][m_name].get("status", "")
            b_val = before_attrs[attr_name][m_name].get("value")
            a_val = after_attrs[attr_name][m_name].get("value")

            status_rank = {"pass": 0, "warning": 1, "fail": 2}
            b_rank = status_rank.get(b_status, 1)
            a_rank = status_rank.get(a_status, 1)

            change = "unchanged"
            if a_rank < b_rank:
                change = "improved"
            elif a_rank > b_rank:
                change = "degraded"
            elif a_val is not None and b_val is not None:
                # If rank is the same, check numeric improvement
                ideal = 1.0 if m_name == "disparate_impact_ratio" else 0.0
                a_diff = abs(a_val - ideal)
                b_diff = abs(b_val - ideal)
                # Use a small epsilon to ignore floating point noise
                if a_diff < b_diff - 0.001:
                    change = "improved"
                elif a_diff > b_diff + 0.001:
                    change = "degraded"
            
            if change == "improved":
                improved += 1
            elif change == "degraded":
                degraded += 1
            else:
                unchanged += 1

            details.append({
                "attribute": attr_name,
                "metric": m_name,
                "before_value": b_val,
                "after_value": a_val,
                "before_status": b_status,
                "after_status": a_status,
                "change": change,
            })

    return {
        "improved": improved,
        "degraded": degraded,
        "unchanged": unchanged,
        "before_risk": before.get("overall_risk_level", "unknown"),
        "after_risk": after.get("overall_risk_level", "unknown"),
        "details": details,
    }


def _record_only_mitigation(db, row, request, recommendations, error_msg=None):
    """Fallback: record the mitigation choice without executing."""
    mitigation_entry = {
        "algorithm": request.algorithm,
        "status": "recorded",
        "success": False,
        "error": error_msg or "Cached data not available for execution",
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
        "status": "recorded",
        "session_id": request.session_id,
        "algorithm_applied": request.algorithm,
        "mitigation_result": mitigation_entry,
        "recommendations": recommendations,
        "message": (
            f"Mitigation '{request.algorithm}' recorded (execution unavailable: "
            f"{error_msg or 'no cached data'})."
        ),
    }


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

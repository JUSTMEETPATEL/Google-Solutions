"""Scan endpoint — accepts model + dataset uploads and runs bias analysis.

Uploads are streamed directly to disk to avoid memory spikes (D-04).
Integrates intersectional analysis, statistical significance, SHAP
feature attribution, plain-English explanations, and auto-recommendations.
Persists results to the session database.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile

from faircheck.analysis.engine import BiasAnalyzer
from faircheck.analysis.explanations import generate_all_explanations
from faircheck.analysis.feature_attribution import compute_feature_attribution
from faircheck.analysis.intersectional import compute_intersectional_analysis
from faircheck.analysis.recommend import recommend_mitigation
from faircheck.analysis.significance import compute_all_confidence_intervals
from faircheck.ai import generate_scan_summary
from faircheck.api.cache import cache_scan_artifacts
from faircheck.config import load_config
from faircheck.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan", tags=["scan"])

_UPLOAD_DIR = Path(tempfile.gettempdir()) / "faircheck_uploads"


def _stream_upload_to_disk(upload: UploadFile) -> Path:
    """Stream an UploadFile to a temporary file on disk and return the path."""
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename).suffix if upload.filename else ""
    dest = tempfile.NamedTemporaryFile(
        dir=_UPLOAD_DIR, suffix=suffix, delete=False
    )
    try:
        shutil.copyfileobj(upload.file, dest)
    finally:
        dest.close()
    return Path(dest.name)


@router.post("/")
async def run_scan(
    model: UploadFile,
    dataset: UploadFile,
) -> dict:
    """Accept a model + dataset, run bias analysis, return structured results."""
    session_id = uuid.uuid4().hex

    # Stream uploads to disk (memory-safe)
    model_path = _stream_upload_to_disk(model)
    dataset_path = _stream_upload_to_disk(dataset)

    try:
        # --- Ingest model + dataset ---
        pipeline = IngestionPipeline()
        ingestion = pipeline.load(
            model_path=model_path,
            data_path=dataset_path,
        )

        # --- Collect full dataset ---
        chunks = list(ingestion.dataset.iter_chunks())
        if not chunks:
            raise HTTPException(status_code=400, detail="Dataset is empty.")
        df = pd.concat(chunks, ignore_index=True)

        # --- Identify feature columns vs protected/target ---
        feature_names = [str(f) for f in (ingestion.model.feature_names_in_ or [])]
        all_cols = set(df.columns)
        feature_set = set(feature_names)

        # Protected attributes: detected by heuristic or extra columns
        detected_protected = ingestion.dataset.detected_protected_attributes
        protected_cols = {
            col for col in detected_protected if col in all_cols
        }

        # Target column: columns not in features and not protected
        non_feature_cols = all_cols - feature_set - protected_cols
        target_col = None
        for candidate in non_feature_cols:
            series = df[candidate]
            nunique = series.nunique()
            if nunique == 2 and series.dtype in (
                np.int64, np.float64, int, float, "int64", "float64",
            ):
                target_col = candidate
                break

        if target_col is None:
            # Fallback: use the last column
            target_col = df.columns[-1]
            logger.warning(
                "Could not auto-detect target column, falling back to '%s'",
                target_col,
            )

        if not protected_cols:
            # If nothing was detected, look for common names
            common_names = {"gender", "sex", "race", "ethnicity", "age_group"}
            protected_cols = all_cols & common_names
            if not protected_cols:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "No protected attributes detected in the dataset. "
                        f"Columns found: {sorted(all_cols)}. "
                        "Expected columns like 'gender', 'race', 'age', etc."
                    ),
                )

        # --- Generate predictions (preserve model's feature order) ---
        ordered_features = [f for f in feature_names if f in all_cols]
        X = df[ordered_features]
        y_true = df[target_col].values
        y_pred = ingestion.model.predict(X)

        y_prob = None
        try:
            y_prob = ingestion.model.predict_proba(X)
            if y_prob is not None and y_prob.ndim == 2:
                y_prob = y_prob[:, 1]  # Take probability of positive class
        except Exception:
            logger.info("Model does not support predict_proba, skipping.")

        # --- Build sensitive features dict ---
        sensitive_features = {
            col: df[col] for col in sorted(protected_cols)
        }

        # --- Run bias analysis ---
        config = load_config()
        analyzer = BiasAnalyzer(config=config)
        analysis = analyzer.analyze(
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
            y_prob=y_prob,
            feature_matrix=X,
        )
        analysis_dict = analysis.to_dict()

        # --- Plain-English explanations ---
        explanations = generate_all_explanations(analysis_dict.get("results", {}))

        # --- Intersectional analysis ---
        intersectional = None
        if len(sensitive_features) >= 2:
            thresholds = config.get("metrics", {}).get("default_thresholds", {})
            try:
                intersectional = compute_intersectional_analysis(
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_features=sensitive_features,
                    thresholds=thresholds,
                )
            except Exception as e:
                logger.warning("Intersectional analysis failed: %s", e)

        # --- Statistical significance (bootstrap CIs) ---
        confidence_intervals = None
        try:
            thresholds = config.get("metrics", {}).get("default_thresholds", {})
            confidence_intervals = compute_all_confidence_intervals(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=sensitive_features,
                n_bootstrap=300,  # Reduced for speed
                thresholds=thresholds,
            )
        except Exception as e:
            logger.warning("Confidence interval computation failed: %s", e)

        # --- Feature attribution ---
        feature_attribution = None
        try:
            feature_attribution = compute_feature_attribution(
                model=ingestion.model._model if hasattr(ingestion.model, '_model') else ingestion.model,
                X=X,
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=sensitive_features,
                feature_names=ordered_features,
                n_repeats=5,
            )
        except Exception as e:
            logger.warning("Feature attribution failed: %s", e)

        # --- Auto-recommend mitigation ---
        recommendations = recommend_mitigation(analysis_dict)

        # --- Gemini compliance summary (optional) ---
        ai_summary = generate_scan_summary(
            model_name=model.filename or "Unknown Model",
            analysis_results=analysis_dict,
            recommendations=recommendations,
        )

        # --- Cache artifacts for mitigation ---
        try:
            cache_scan_artifacts(
                session_id=session_id,
                model_path=model_path,
                dataset_path=dataset_path,
                feature_names=ordered_features,
                protected_cols=sorted(protected_cols),
                target_col=target_col,
            )
        except Exception as e:
            logger.warning("Artifact caching failed: %s", e)

        # --- Persist to database ---
        model_name = model.filename or "Unknown Model"
        try:
            _persist_session(
                session_id=session_id,
                model_name=model_name,
                analysis_dict=analysis_dict,
                explanations=explanations,
                intersectional=intersectional,
                confidence_intervals=confidence_intervals,
                feature_attribution=feature_attribution,
                recommendations=recommendations,
                ai_summary=ai_summary,
            )
        except Exception as e:
            logger.warning("Session persistence failed: %s", e)

        return {
            "session_id": session_id,
            "status": "complete",
            "model_name": model_name,
            "analysis_results": analysis_dict,
            "explanations": explanations,
            "intersectional_analysis": intersectional,
            "confidence_intervals": confidence_intervals,
            "feature_attribution": feature_attribution,
            "recommendations": recommendations,
            "ai_summary": ai_summary,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Scan failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        # Cleanup temp files
        for p in (model_path, dataset_path):
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass


def _persist_session(
    session_id: str,
    model_name: str,
    analysis_dict: dict,
    explanations: dict,
    intersectional: dict | None,
    confidence_intervals: dict | None,
    feature_attribution: dict | None,
    recommendations: list,
    ai_summary: dict,
) -> None:
    """Save scan results to the SQLite database."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        session_row = SessionModel(
            id=session_id,
            status="complete",
            model_path=model_name,
            dataset_path="uploaded",
            risk_level=analysis_dict.get("overall_risk_level", "unknown"),
            bias_metrics={
                "analysis_results": analysis_dict,
                "explanations": explanations,
                "intersectional_analysis": intersectional,
                "confidence_intervals": confidence_intervals,
                "feature_attribution": feature_attribution,
                "recommendations": recommendations,
                "ai_summary": ai_summary,
            },
        )
        db.add(session_row)
        db.commit()
        logger.info("Session %s persisted to database", session_id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

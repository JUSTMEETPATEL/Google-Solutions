"""Report generation endpoint — PDF, Markdown, DOCX.

Generates compliance-ready audit reports from stored session data.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRequest(BaseModel):
    """Request body for report generation."""
    session_id: str
    format: str = "pdf"  # pdf | md | docx
    regulation: str | None = "eu_ai_act"


def _get_db():
    """Lazy-import DB to avoid circular imports at module load."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.post("/")
async def generate_report(request: ReportRequest) -> FileResponse:
    """Generate a regulation-ready audit report.

    Accepts a session ID, format, and optional regulation standard.
    Returns the generated file as a download.
    """
    if request.format not in ("pdf", "md", "docx"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{request.format}'. Use 'pdf', 'md', or 'docx'.",
        )

    SessionLocal, SessionModel = _get_db()
    db = SessionLocal()

    try:
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
                detail="Session has no analysis results for report generation.",
            )

        # Build report data dict
        report_data = {
            "session_id": row.id,
            "model_name": row.model_path or "Unknown Model",
            "model_version": "1.0",
            "analysis_results": analysis_results,
            "mitigation": (
                row.mitigation_history[-1] if row.mitigation_history else None
            ),
            "oversight": (
                {"decision": row.oversight_decision} if row.oversight_decision else None
            ),
            "regulation_standard": request.regulation or "EU AI Act",
        }

        from faircheck.reports.renderers import ReportBuilder
        builder = ReportBuilder()
        results = builder.build(
            data=report_data,
            formats=[request.format],
            regulation=request.regulation,
        )

        out_path = results.get(request.format)
        if out_path is None or not out_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Report generation completed but file not found.",
            )

        media_types = {
            "pdf": "application/pdf",
            "md": "text/markdown",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        return FileResponse(
            path=str(out_path),
            media_type=media_types.get(request.format, "application/octet-stream"),
            filename=f"faircheck-report-{row.id[:8]}.{request.format}",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        db.close()

"""Report generation endpoint — PDF, HTML, Markdown, DOCX.

Generates compliance-ready audit reports from stored session data.
Now includes WCAG AA accessible HTML output.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRequest(BaseModel):
    """Request body for report generation."""
    session_id: str
    format: str = "pdf"  # pdf | md | docx | html
    regulation: str | None = "eu_ai_act"


def _get_db():
    """Lazy-import DB to avoid circular imports at module load."""
    from faircheck.api.db import SessionLocal, engine, Base
    from faircheck.api.models import Session as SessionModel
    Base.metadata.create_all(bind=engine)
    return SessionLocal, SessionModel


@router.post("/", response_model=None)
async def generate_report(request: ReportRequest):
    """Generate a regulation-ready audit report.

    Accepts a session ID, format, and optional regulation standard.
    Returns the generated file as a download (or inline HTML for 'html' format).
    """
    valid_formats = ("pdf", "md", "docx", "html")
    if request.format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{request.format}'. Use one of: {', '.join(valid_formats)}.",
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
            "mitigation": bias_metrics.get("mitigation"),
            "mitigation_history": row.mitigation_history or [],
            "oversight": (
                bias_metrics.get("oversight") or
                ({"decision": row.oversight_decision} if row.oversight_decision else None)
            ),
            "regulation_standard": request.regulation or "EU AI Act",
            "intersectional_analysis": bias_metrics.get("intersectional_analysis"),
            "confidence_intervals": bias_metrics.get("confidence_intervals"),
            "feature_attribution": bias_metrics.get("feature_attribution"),
            "recommendations": bias_metrics.get("recommendations", []),
            "explanations": bias_metrics.get("explanations", {}),
            "ai_summary": bias_metrics.get("ai_summary"),
        }

        from faircheck.reports.renderers import ReportBuilder
        builder = ReportBuilder()

        # HTML format returns inline
        if request.format == "html":
            html_content = builder.build_html_accessible(
                data=report_data,
                regulation=request.regulation,
            )
            return HTMLResponse(content=html_content)

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

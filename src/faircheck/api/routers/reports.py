"""Report generation endpoint.

Triggers PDF/DOCX report generation for a scan session.
Stub — full implementation deferred until the reporting phase.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/")
async def generate_report() -> dict:
    """Generate a regulation-ready audit report.

    Stub — will be implemented in the reporting phase.
    """
    return {"status": "report_pending", "message": "Not yet implemented."}

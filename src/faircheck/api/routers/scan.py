"""Scan endpoint — accepts model + dataset uploads and runs bias analysis.

Uploads are streamed directly to disk to avoid memory spikes (D-04).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

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
    """Accept a model + dataset, run bias analysis, return structured results.

    Currently returns a placeholder while the full pipeline integration
    is pending Phase 3 (Bias Analysis Engine) completion.
    """
    # Stream uploads to disk (memory-safe)
    model_path = _stream_upload_to_disk(model)
    dataset_path = _stream_upload_to_disk(dataset)

    # TODO: Integrate with IngestionPipeline + BiasAnalysisEngine
    # once Phase 3 is complete.
    return {
        "status": "scan_received",
        "model_file": model_path.name,
        "dataset_file": dataset_path.name,
        "message": "Bias analysis pipeline integration pending Phase 3.",
    }

"""Report data contract (D-03).

The report builder accepts a plain dict from ``AnalysisResult.to_dict()``
or stored session JSON.  ``ReportData`` normalizes this into typed fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReportData:
    """Typed container for all data needed to render a report."""

    # Cover page (RPT-01)
    model_name: str = "Unknown Model"
    model_version: str = "1.0"
    audit_date: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    reviewer: str = ""
    regulation_standard: str = "EU AI Act"

    # Model card (RPT-03)
    training_data_description: str = ""
    intended_use: str = ""
    known_limitations: str = ""

    # Analysis results (RPT-04, RPT-05)
    analysis_results: dict[str, Any] = field(default_factory=dict)

    # Mitigation (RPT-06) — None = placeholder shown (D-06)
    mitigation: dict[str, Any] | None = None

    # Oversight (RPT-07) — None = placeholder shown (D-06)
    oversight: dict[str, Any] | None = None

    # Session metadata
    session_id: str = ""

    # Chart images (base64 PNGs, populated by chart module)
    chart_images: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportData:
        """Build ``ReportData`` from a plain dict."""
        return cls(
            model_name=data.get("model_name", "Unknown Model"),
            model_version=data.get("model_version", "1.0"),
            audit_date=data.get(
                "audit_date",
                datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            ),
            reviewer=data.get("reviewer", ""),
            regulation_standard=data.get("regulation_standard", "EU AI Act"),
            training_data_description=data.get("training_data_description", ""),
            intended_use=data.get("intended_use", ""),
            known_limitations=data.get("known_limitations", ""),
            analysis_results=data.get("analysis_results", {}),
            mitigation=data.get("mitigation"),
            oversight=data.get("oversight"),
            session_id=data.get("session_id", ""),
            chart_images=data.get("chart_images", {}),
        )

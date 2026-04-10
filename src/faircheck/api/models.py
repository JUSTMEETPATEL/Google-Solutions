"""SQLAlchemy ORM models for FairCheck session persistence.

Defines the ``Session`` model that stores scan results, bias metrics,
and mitigation history in the local SQLite database.

SESS-02: Session includes model metadata, dataset metadata, metric results,
          timestamps.
SESS-03: Queryable fields for session listing (model_path, risk_level,
          created_at).
SESS-05: ``mitigation_history`` JSON column stores algorithm applied,
          before/after metrics.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, JSON, String

from faircheck.api.db import Base


def _utcnow() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class Session(Base):
    """A single bias-audit session.

    Each scan run produces exactly one Session row.  The row tracks
    everything needed for the compliance report and the session-list UI.
    """

    __tablename__ = "sessions"

    # ── Identity ──────────────────────────────────────────────────────
    id: str = Column(String, primary_key=True)  # UUID string

    # ── State machine ─────────────────────────────────────────────────
    status: str = Column(String, nullable=False, default="pending")
    # Valid values: pending | running | complete | failed

    # ── Input references (absolute paths — D-04) ─────────────────────
    model_path: str = Column(String, nullable=False)
    dataset_path: str = Column(String, nullable=False)

    # ── Results ───────────────────────────────────────────────────────
    risk_level: str = Column(String, default="unknown")
    # high | medium | low | unknown

    bias_metrics = Column(JSON, nullable=True)
    # Deeply nested dict from Fairlearn/AIF360 — stored as-is (D-03).

    mitigation_history = Column(JSON, nullable=True)
    # List of dicts: [{"algorithm": "...", "before": {...}, "after": {...}}]

    # ── Oversight ─────────────────────────────────────────────────────
    oversight_decision: str | None = Column(String, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────
    created_at: datetime = Column(DateTime, default=_utcnow)
    updated_at: datetime = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<Session id={self.id!r} status={self.status!r} "
            f"risk={self.risk_level!r}>"
        )

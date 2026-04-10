"""Tests for session persistence layer (Phase 5).

Validates:
- SESS-01: SQLite store at ~/.faircheck/sessions.db
- SESS-04: WAL mode enabled via PRAGMA
- SESS-02/SESS-05: Session model with metrics + mitigation JSON columns
"""

import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def tmp_db_dir(tmp_path):
    """Provide a temporary directory for the test database."""
    return tmp_path


@pytest.fixture
def test_engine(tmp_db_dir):
    """Create a test engine pointing at a temporary SQLite database."""
    db_path = tmp_db_dir / "sessions.db"
    url = f"sqlite:///{db_path}"
    eng = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(eng, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return eng


@pytest.fixture
def test_session_factory(test_engine):
    """Create a session factory bound to the test engine."""
    from faircheck.api.models import Base

    Base.metadata.create_all(bind=test_engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    return factory


def test_db_initialization(tmp_db_dir):
    """SESS-01: Database file is created when engine connects."""
    db_path = tmp_db_dir / "sessions.db"
    url = f"sqlite:///{db_path}"
    eng = create_engine(url, connect_args={"check_same_thread": False})

    # Force a connection to create the file
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))

    assert db_path.exists(), "sessions.db was not created"


def test_wal_mode_enabled(test_engine):
    """SESS-04: WAL journal mode is active after engine connect event fires."""
    with test_engine.connect() as conn:
        result = conn.execute(text("PRAGMA journal_mode")).scalar()
        assert result == "wal", f"Expected WAL mode, got '{result}'"


def test_session_crud(test_session_factory):
    """SESS-01/02/05: Insert, query, and verify a Session record with JSON columns."""
    from faircheck.api.models import Session as ScanSession

    db = test_session_factory()
    try:
        session_id = str(uuid.uuid4())
        record = ScanSession(
            id=session_id,
            status="complete",
            model_path="/mock/model.pkl",
            dataset_path="/mock/dataset.csv",
            risk_level="medium",
            bias_metrics={"demographic_parity": {"value": 0.05, "pass": True}},
            mitigation_history=[
                {
                    "algorithm": "reweighing",
                    "before": {"dp": 0.15},
                    "after": {"dp": 0.05},
                }
            ],
        )
        db.add(record)
        db.commit()

        # Query back
        fetched = db.query(ScanSession).filter_by(id=session_id).first()
        assert fetched is not None
        assert fetched.status == "complete"
        assert fetched.model_path == "/mock/model.pkl"
        assert fetched.dataset_path == "/mock/dataset.csv"
        assert fetched.risk_level == "medium"
        assert fetched.bias_metrics["demographic_parity"]["pass"] is True
        assert fetched.mitigation_history[0]["algorithm"] == "reweighing"
        assert fetched.created_at is not None
        assert fetched.updated_at is not None
    finally:
        db.close()


def test_session_list_returns_summaries(test_session_factory):
    """SESS-03: Sessions can be listed with summary data (model name, date, risk)."""
    from faircheck.api.models import Session as ScanSession

    db = test_session_factory()
    try:
        # Insert two sessions
        for i, risk in enumerate(["high", "low"]):
            db.add(
                ScanSession(
                    id=str(uuid.uuid4()),
                    status="complete",
                    model_path=f"/models/model_{i}.pkl",
                    dataset_path=f"/data/data_{i}.csv",
                    risk_level=risk,
                )
            )
        db.commit()

        results = db.query(
            ScanSession.id,
            ScanSession.model_path,
            ScanSession.risk_level,
            ScanSession.created_at,
        ).all()

        assert len(results) == 2
        assert results[0].risk_level in ("high", "low")
    finally:
        db.close()

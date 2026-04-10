"""Database connection and session management for FairCheck.

Configures a local SQLite database at ~/.faircheck/sessions.db with WAL
journal mode for safe concurrent access between the TUI and Web interfaces.

Usage in FastAPI routers::

    from faircheck.api.db import get_db
    from sqlalchemy.orm import Session

    @router.get("/")
    def list_items(db: Session = Depends(get_db)):
        ...
"""

from __future__ import annotations

import pathlib
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ---------------------------------------------------------------------------
# Database location — always local-first under ~/.faircheck/
# ---------------------------------------------------------------------------
DB_DIR: pathlib.Path = pathlib.Path.home() / ".faircheck"
DB_DIR.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL: str = f"sqlite:///{DB_DIR}/sessions.db"

# ---------------------------------------------------------------------------
# Engine — check_same_thread=False required for FastAPI (multi-thread access)
# ---------------------------------------------------------------------------
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ANN001
    """Enable WAL journal mode and relaxed synchronous for performance.

    SESS-04: WAL prevents write contention between TUI and Web processes.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------------------------
# Declarative base for ORM models
# ---------------------------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI dependency — standard Depends(get_db) pattern
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

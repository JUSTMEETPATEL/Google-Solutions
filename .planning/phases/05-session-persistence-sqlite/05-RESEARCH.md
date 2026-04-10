# Phase 05: Session Persistence (SQLite) - Research

## Context Analysis

The goal of this phase is to establish the local SQLite database for the FairCheck application using SQLAlchemy.
This database is the single source of truth for both the TUI interface and the Web application (acting via the FastAPI backend).
It must track:
1. Sessions (model metadata, dataset metadata, risk levels, states).
2. Scan Results/Metrics (nested dictionaries of Fairlearn/AIF360 results).
3. Mitigation History.

## Database & ORM Approach

- **SQLite + WAL Mode**: Requirement SESS-04 explicitly mandates WAL (Write-Ahead Logging) mode. This requires configuring standard SQLite engine parameters in SQLAlchemy (`PRAGMA journal_mode=WAL;`).
- **Synchronous SQLAlchemy**: We decided in Phase 04 to keep FastAPI routes blocked and purely synchronous since this is a local utility. Thus, we'll use `sqlite3` without asynchronous drivers like `aiosqlite`.
- **Alembic**: We elected to use Alembic for proper schema migrations. We need to initialize an Alembic environment (`alembic init alembic`) and define the models.

## Schema Architecture

We need a central `Session` ORM model.
Given the decisions from the context:
- `id`: Primary key (UUID string recommended to prevent ID guessing and simplify TUI/Web handoff).
- `status`: String representation of explicit state (`pending`, `running`, `complete`, `failed`).
- `model_path`: Absolute path to the model file.
- `dataset_path`: Absolute path to the dataset file.
- `created_at` / `updated_at`: Timestamps.
- `risk_level`: String (`high`, `medium`, `low`, `unknown`).
- `bias_metrics`: JSON column (`sqlalchemy.JSON`).
- `mitigation_history`: JSON column, or a separate related table `MitigationEvent`. Storing it as JSON inside `Session` is simplest to satisfy SESS-05, e.g., `[{"algorithm": "reweighing", "before": {...}, "after": {...}}]`.
- `oversight_decision`: JSON column or string for the future WEB-07 human oversight log.

## FastAPI Integration

We'll use standard `Depends(get_db)` dependency injection:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
This requires configuring `sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
We need an event listener or `connect_args={'check_same_thread': False}` setup along with `execute("PRAGMA journal_mode=WAL")`.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

# Enable WAL mode on connect
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
```

## Validation Architecture

To satisfy Nyquist validation capabilities (Dimension 8), we must verify that:
1. The SQLite database is created at `~/.faircheck/sessions.db`.
2. WAL mode is actually active.
3. The schema allows JSON columns to read/write complex metric structures effectively.
4. FastAPI endpoints correctly acquire and release the database session.
5. Alembic can generate effectively the first migration and apply it.

*This concludes the research for Phase 5.*

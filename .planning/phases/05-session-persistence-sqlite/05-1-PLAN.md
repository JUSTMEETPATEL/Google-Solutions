---
wave: 1
depends_on: []
files_modified:
  - tests/api/test_sessions_persistence.py
  - src/faircheck/api/db.py
  - src/faircheck/api/models.py
  - alembic.ini
  - alembic/env.py
autonomous: true
---

# Phase 05: Session Persistence (SQLite) - Plan

## Requirements Covered
- **SESS-01**: local SQLite store at ~/.faircheck/sessions.db
- **SESS-02**: Session includes model, dataset, metrics, timestamps
- **SESS-03**: List past sessions summary
- **SESS-04**: SQLite runs in WAL mode
- **SESS-05**: Mitigation history stored in Session data
- **DIM-8**: Verification tracking (Nyquist)

## Execution Plan

<task id="05-01-01" requirements="SESS-01, SESS-04">
  <action>
    Create test stub `tests/api/test_sessions_persistence.py` to assert that `faircheck.api.db` initializes the database at `~/.faircheck/sessions.db` and configures `PRAGMA journal_mode=WAL` exactly as written.
  </action>
  <read_first>
    - .planning/phases/05-session-persistence-sqlite/05-VALIDATION.md
  </read_first>
  <acceptance_criteria>
    - `tests/api/test_sessions_persistence.py` exists
    - File contains `def test_db_initialization(`
    - File contains `def test_wal_mode_enabled(`
  </acceptance_criteria>
</task>

<task id="05-01-02" requirements="SESS-01, SESS-04">
  <action>
    Implement Database Connection Module in `src/faircheck/api/db.py`:
    1. Import `sqlalchemy` and standard libraries (`os`, `pathlib`).
    2. Set `DB_DIR = pathlib.Path.home() / ".faircheck"` and ensure the directory exists (`mkdir(parents=True, exist_ok=True)`).
    3. Define `SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}/sessions.db"`
    4. Create engine: `engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})`.
    5. Set WAL mode via SQLAlchemy event listener on `connect`: `cursor.execute("PRAGMA journal_mode=WAL")` and `cursor.execute("PRAGMA synchronous=NORMAL")`.
    6. Define `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
    7. Define `Base = declarative_base()`
    8. Write `get_db()` generator that yields `SessionLocal()` and safely closes (`finally: db.close()`).
  </action>
  <read_first>
    - tests/api/test_sessions_persistence.py
  </read_first>
  <acceptance_criteria>
    - `src/faircheck/api/db.py` contains `engine = create_engine`
    - `src/faircheck/api/db.py` contains `cursor.execute("PRAGMA journal_mode=WAL")`
    - `src/faircheck/api/db.py` contains `def get_db():`
  </acceptance_criteria>
</task>

<task id="05-01-03" requirements="SESS-02, SESS-03, SESS-05">
  <action>
    Implement Database Models in `src/faircheck/api/models.py`:
    1. Import `Base` from `faircheck.api.db`.
    2. Import `Column, String, JSON, DateTime` from `sqlalchemy`.
    3. Define class `Session(Base)` with `__tablename__ = "sessions"`.
    4. Add columns:
       - `id`: `String` (primary_key=True) (will hold UUIDs)
       - `status`: `String` (nullable=False, default="pending")
       - `model_path`: `String` (nullable=False)
       - `dataset_path`: `String` (nullable=False)
       - `risk_level`: `String` (default="unknown")
       - `bias_metrics`: `JSON` (nullable=True)
       - `mitigation_history`: `JSON` (nullable=True)
       - `oversight_decision`: `String` (nullable=True)
       - `created_at`: `DateTime` (default=datetime.utcnow)
       - `updated_at`: `DateTime` (default=datetime.utcnow, onupdate=datetime.utcnow)
  </action>
  <read_first>
    - src/faircheck/api/db.py
  </read_first>
  <acceptance_criteria>
    - `src/faircheck/api/models.py` contains `class Session(Base):`
    - File contains `__tablename__ = "sessions"`
    - File contains `bias_metrics = Column(JSON`
    - File contains `mitigation_history = Column(JSON`
  </acceptance_criteria>
</task>

<task id="05-01-04" requirements="SESS-01">
  <action>
    Initialize Alembic locally (since this is an audit tool, Alembic should generate its environment in the CLI codebase to support schema tracking for users over time, or just locally in the repo for schema generation):
    1. Run `alembic init alembic` from the project root.
    2. Overwrite `alembic.ini` configuration parameter `sqlalchemy.url` to use the dynamic FairCheck path: replace the hardcoded `sqlalchemy.url` line in `alembic.ini` so it isn't statically pointing to a fake file. (Usually Alembic is configured via `env.py` directly).
    3. Edit `alembic/env.py` to dynamically locate the DB. Import `DB_DIR` from `faircheck.api.db` and the models Base.
    4. In `env.py`, set:
       ```python
       import sys
       import os
       sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
       from src.faircheck.api.db import DB_DIR, Base
       from src.faircheck.api import models
       target_metadata = Base.metadata
       
       config.set_main_option('sqlalchemy.url', f"sqlite:///{DB_DIR}/sessions.db")
       ```
    5. Run `alembic revision --autogenerate -m "Initial Schema"` to create the first migration.
  </action>
  <read_first>
    - src/faircheck/api/models.py
  </read_first>
  <acceptance_criteria>
    - `alembic/env.py` contains `from src.faircheck.api.db import DB_DIR`
    - `alembic/env.py` contains `target_metadata = Base.metadata`
    - A migration file exists in `alembic/versions/`
  </acceptance_criteria>
</task>

<task id="05-01-05" requirements="SESS-01">
  <action>
    Implement validation: update the tests in `tests/api/test_sessions_persistence.py` to actually test the created models. Write tests that instantiate a `SessionLocal`, insert a mock `models.Session` with `status="complete"`, `model_path="/mock"`, etc., commit it, query it, and assert the values. Clean up the DB stub file after the test.
  </action>
  <read_first>
    - tests/api/test_sessions_persistence.py
    - src/faircheck/api/models.py
    - src/faircheck/api/db.py
  </read_first>
  <acceptance_criteria>
    - `pytest tests/api/test_sessions_persistence.py` passes gracefully
    - Test function `test_session_crud` exists
  </acceptance_criteria>
</task>

---

## Verification

<threat_model>
- Ensure WAL PRAGMA cannot lead to arbitrary code execution if SQLite drivers mismatch.
</threat_model>

<must_haves>
- Database initializes in `~/.faircheck/sessions.db`
- WAL mode explicitly PRAGMA executed
- `Session` model contains `bias_metrics` and `mitigation_history` as JSON types.
</must_haves>

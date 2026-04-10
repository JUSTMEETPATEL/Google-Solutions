# Phase 05: Session Persistence (SQLite) - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the local database storage layer using SQLAlchemy to persist scan results, model/dataset metadata, and mitigation history in `~/.faircheck/sessions.db`.
</domain>

<decisions>
## Implementation Decisions

### Database Core
- **D-01:** **Migrations:** Use Alembic Migrations for tracking and applying schema evolution.
- **D-02:** **Concurrency:** Use standard Synchronous SQLAlchemy (aligns with the blocking approach decided in Phase 4).

### Schema & Data Storage
- **D-03:** **Metrics Format:** Store bias metric results natively in JSON Columns, keeping the DB simple while supporting the deeply nested/variable structures Fairlearn/AIF360 output.
- **D-04:** **File Referencing:** Store absolute paths to the user's uploaded model and dataset files to easily re-load them later.
- **D-05:** **Session States:** Implement explicit state tracking (e.g. `pending`, `running`, `complete`, `failed`) rather than purely final results, enabling accurate audit logs.

### Lifecycle & Retention
- **D-06:** **Retention Policy:** Implement indefinite retention for sessions (no auto-delete). Audits are generally meant to be kept forever.
- **D-07:** **Session Injection:** Use the standard FastAPI `Depends(get_db)` generator pattern for automatically managing DB session lifecycles during requests.

### the agent's Discretion
- None explicitly requested, standard execution expected.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Requirements
- `.planning/PROJECT.md` — Overall architecture constraints and goal (Local-first, Python 3.11).
- `.planning/REQUIREMENTS.md` — Phase 5 requirements (SESS-01 to SESS-05).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None.

### Established Patterns
- Phase 4 established synchronous endpoints which perfectly unifies with the synchronous SQLAlchemy DB pattern selected here.

### Integration Points
- `src/faircheck/api/routers/sessions.py` (Currently stubs, will be backed by the DB queries).
- `src/faircheck/api/routers/scan.py` (Needs to generate the initial session record and set state to `running` then `complete`).

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.
</specifics>

<deferred>
## Deferred Ideas

- Session cleanup or auto-delete TTLs are deferred to a potential v2 feature.
</deferred>

---

*Phase: 05-session-persistence-sqlite*
*Context gathered: 2026-04-10*

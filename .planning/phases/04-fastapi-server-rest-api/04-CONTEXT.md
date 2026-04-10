# Phase 04: FastAPI Server & REST API - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Wrap the engine in a FastAPI server exposing REST endpoints for scanning, sessions, reporting, and lifecycle management.
</domain>

<decisions>
## Implementation Decisions

### API Architecture
- **D-01:** **Modular Routing:** Create `src/faircheck/api/routers/` with separate files for `scan`, `sessions`, `reports`, etc.
- **D-02:** **API Versioning:** Use URL path versioning by prepending `/api/v1/` to all endpoints (e.g., `/api/v1/scan`).
- **D-03:** **Server Execution:** Use a Python script programmatic wrapper that calls `uvicorn.run()` on an available port, writing the port to `~/.faircheck/port`.

### Data & Payload Handling
- **D-04:** **Upload Memory Handling:** Stream datasets directly to disk (e.g., in `/tmp/faircheck_uploads/`) rather than using SpooledTemporaryFile to avoid memory spikes.
- **D-05:** **Error Formatting:** Use RFC 7807 Problem Details standards to return structured error JSON (giving it strongly typed parsing guarantees for TUI & Web logic).
- **D-06:** **CORS Policy:** Use Allow-All `*` since this is a local-first single-user tool, preventing domain/port blockades from Vite.
- **D-07:** **Long-Running Tasks:** Use Synchronous Blocking for mitigation and long scans (simplest approach for v1 given it’s a single-user local tool, avoiding complex WebSockets/Polling).

### Prior Decisions Kept
- **D-08:** **Strict validation (fail loudly):** Continue returning immediate 400 validations for schema or NaN discrepancies in data uploads (from Phase 2).

### the agent's Discretion
None explicitly noted. Follow the standard best practices for FastAPI local applications.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Requirements
- `.planning/PROJECT.md` — Overall architecture constraints and goal (Local-only, FastAPI, Python 3.11).
- `.planning/REQUIREMENTS.md` — Phase 4 requirements (API-01 to API-08).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/faircheck/ingestion/pipeline.py` provides the logic that the new POST `/api/v1/scan` endpoint should invoke.

### Established Patterns
- Rely on Pydantic models for request ingestion.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.
</deferred>

---

*Phase: 04-fastapi-server-rest-api*
*Context gathered: 2026-04-10*

# Phase 4: FastAPI Server & REST API - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 4 - FastAPI Server & REST API
**Areas discussed:** API Routing Structure, Server Execution Pattern, Upload Memory Handling, Error Response Format, API Versioning Strategy, CORS Policy, Long-Running Task Handling

---

## API Routing Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Modular | Create `src/faircheck/api/routers/` with separate files | ✓ |
| Single File | All endpoints in `main.py` | |

**User's choice:** 1

---

## Server Execution Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Programmatic Wrapper | Call `uvicorn.run()` programmatically, write to `~/.faircheck/port` | ✓ |
| CLI Driven | `uvicorn src...main:app --port 8000` via terminal| |

**User's choice:** 1

---

## Upload Memory Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Stream directly to disk | Write upload straight to temporary file | ✓ |
| SpooledTemporaryFile | Default FastAPI spooling mechanics | |

**User's choice:** 1

---

## Error Response Format

| Option | Description | Selected |
|--------|-------------|----------|
| RFC 7807 Problem Details | Standardized structured format | ✓ |
| Standard FastAPI Exceptions | Simple default format `{"detail": "..."}` | |

**User's choice:** 1

---

## API Versioning Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| URL path versioning | Prepend `/api/v1/` to all endpoints | ✓ |
| No explicit versioning | Just use `/api/scan` | |

**User's choice:** 1

---

## CORS Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Allow-All `*` | Prevent local dev blockades | ✓ |
| Strict Whitelist | Limit specifically to localhost:5173 | |

**User's choice:** 1

---

## Long-Running Task Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Synchronous Blocking | Wait for mitigation/scan and return HTTP 200 result (simplest local approach) | ✓ |
| FastAPI BackgroundTasks| Return 202 quickly and background the process | |

**User's choice:** 1

---

## the agent's Discretion

None explicitly named.

## Deferred Ideas

None recorded.

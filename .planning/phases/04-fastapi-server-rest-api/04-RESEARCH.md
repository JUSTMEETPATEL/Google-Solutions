# Phase 04 Research: FastAPI Server & REST API

## Technical Approach & Domain Exploration

This document identifies implementation patterns, constraints, and dependencies needed to safely plan Phase 04.

### 1. New Dependencies Required
The current `pyproject.toml` is missing the web tier packages.
- **`fastapi`** — the core framework.
- **`uvicorn`** — the ASGI server to run FastAPI programmatically.
- **`python-multipart`** — required by FastAPI to parse `multipart/form-data` which is necessary for the `UploadFile` (model and dataset uploads).

### 2. Programmatic Execution & Port Discovery (D-03)
The API must start programmatically and write its bound port to `~/.faircheck/port`. This avoids static port collisions.

**Implementation Strategy:**
```python
import socket
import uvicorn
from pathlib import Path
from faircheck.api.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def serve():
    port = find_free_port()
    port_file = Path.home() / ".faircheck" / "port"
    port_file.parent.mkdir(exist_ok=True)
    port_file.write_text(str(port))
    
    # Run uvicorn programmatically
    uvicorn.run(app, host="127.0.0.1", port=port)
```

### 3. Modular Routing Structure (D-01 & D-02)
We'll create multiple API routers to isolate endpoints and apply the `/api/v1` prefix.

**Folder Structure:**
`src/faircheck/api/`
  `main.py` -> mounts all routers, configures CORS, custom exception handlers.
  `routers/`
    `scan.py` -> `POST /api/v1/scan`
    `sessions.py` -> `GET /api/v1/sessions`, `GET /api/v1/sessions/{id}`
    `mitigate.py` -> `POST /api/v1/mitigate`
    `reports.py` -> `POST /api/v1/report`
    `oversight.py` -> `POST /api/v1/oversight`
    `health.py` -> `GET /api/v1/health`

### 4. Upload Memory Handling (D-04)
To avoid massive memory spikes (Gigabyte-sized parquets), we must strictly stream the upload to disk before handing it off to the ingestion pipeline (`DatasetChunker`). 

**Implementation Strategy:**
Instead of `file.file.read()`, we read in chunks and write to a `tempfile.NamedTemporaryFile` with `delete=False`, passing the valid path to `DatasetChunker`.

### 5. Standardized Error Handling (D-05)
Replace the default FastAPI exception handlers with RFC 7807 structured format handlers so the TUI and Frontend receive:
```json
{
  "type": "https://faircheck.dev/errors/validation",
  "title": "Invalid Data",
  "status": 400,
  "detail": "Data contains NaN values.",
  "instance": "/api/v1/scan"
}
```
*Note: We can easily achieve this by overriding `RequestValidationError` and `StarletteHTTPException` locally in `main.py` without requiring an extraneous dependency.*

### 6. CORS Policy (D-06)
Since Vite will run on port `5173` locally, we must use `fastapi.middleware.cors.CORSMiddleware` in `main.py` allowing `allow_origins=["*"]`, `allow_methods=["*"]`, and `allow_headers=["*"]`.

### 7. Synchronous Blocking Execution (D-07)
Scans and bias mitigations will NOT be offloaded to BackgroundTasks (as decided). The router endpoints will directly await or perform the heavy computation and not return `200 OK` until complete.

### 8. Phase 2 Dependencies
- The `POST /api/v1/scan` endpoint directly relies upon `src/faircheck/ingestion/pipeline.py`.
- Because session persistence (SQLite) is slated for **Phase 5**, the GET endpoints (`/sessions` etc.) will return empty or mocked data structures in Phase 4.

## Validation Architecture
- **Dependency checks:** Verify `uv sync` correctly installs `fastapi[standard]` and `python-multipart`.
- **Health Check:** `curl -s localhost:$(cat ~/.faircheck/port)/api/v1/health` returns `200`.
- **End-to-End Routing Validation:** Use `pytest` with `TestClient` from `fastapi.testclient` to ensure all 7 required endpoint routes evaluate cleanly (200, 404, or 422 if payload is missing) without 500 crashes.
- **Error Formatting Validation:** Trigger a validation error intentionally to verify RFC 7807 structured response structure.

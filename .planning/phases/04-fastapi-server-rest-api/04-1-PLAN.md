---
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - src/faircheck/api/server.py
  - src/faircheck/api/main.py
  - src/faircheck/api/errors.py
  - src/faircheck/api/routers/__init__.py
  - src/faircheck/api/routers/health.py
  - src/faircheck/api/routers/scan.py
  - src/faircheck/api/routers/sessions.py
  - src/faircheck/api/routers/mitigate.py
  - src/faircheck/api/routers/reports.py
  - src/faircheck/api/routers/oversight.py
  - tests/api/test_health.py
autonomous: true
---

# 04-1-PLAN: FastAPI Foundation & Endpoints

<objective>
Implement the FastAPI server core, programmatic port discovery, structured RFC 7807 error handling, and wire up all required REST API routers matching the Phase 4 requirements and context decisions.
</objective>

<threat_model>
- **T-04-01 | Denial of Service via large uploads:** Upload endpoint maps straight to `tempfile.NamedTemporaryFile` instead of in-memory spools to prevent OOM errors.
- **T-04-02 | CORS Misconfiguration:** By design (D-06) CORS is completely open `allow_origins=["*"]` since this is a local-only CLI tool where localhost restrictions often break depending on frontend toolchains.
</threat_model>

<task>
<id>04-01-01</id>
<title>Add FastAPI dependencies</title>
<read_first>
- pyproject.toml
</read_first>
<action>
Modify `pyproject.toml` to add `fastapi[standard]>=0.115.0` and `python-multipart>=0.0.9` to `dependencies`. Add `httpx>=0.27.0` to `dev` dependency-groups (required for `TestClient`).
Run `uv sync` to apply the updates.
</action>
<acceptance_criteria>
- `pyproject.toml` contains `"fastapi[standard]>=0.115.0"`
- `uv sync` exits 0
</acceptance_criteria>
</task>

<task>
<id>04-01-02</id>
<title>Implement RFC 7807 structured errors</title>
<read_first>
- 04-RESEARCH.md
</read_first>
<action>
Create `src/faircheck/api/errors.py`.
Define Pydantic schema `ProblemDetails` with fields `type`, `title`, `status`, `detail`, `instance`.
Implement exception handlers for `StarletteHTTPException` and `RequestValidationError` that return `JSONResponse(content=ProblemDetails(...).model_dump(), status_code=status_code)`.
</action>
<acceptance_criteria>
- `src/faircheck/api/errors.py` contains `class ProblemDetails`
- `src/faircheck/api/errors.py` contains exception overrides returning `JSONResponse` with RFC 7807 fields.
</acceptance_criteria>
</task>

<task>
<id>04-01-03</id>
<title>Create API routers</title>
<read_first>
- 04-CONTEXT.md
</read_first>
<action>
Create directory `src/faircheck/api/routers/`. Create `__init__.py`.
Create `health.py` containing a simple `router = APIRouter(prefix="/health")` and `GET /` returning `{"status": "ok"}`.
Create `scan.py` containing `router = APIRouter(prefix="/scan")` and a `POST /` endpoint accepting `UploadFile` parameters for model and dataset using memory-safe standard chunked file writing, responding with `{"status": "placeholder for pipeline"}` for now.
Create bare routers for the remaining requirements:
- `sessions.py`: `GET /` and `GET /{id}`
- `mitigate.py`: `POST /`
- `reports.py`: `POST /`
- `oversight.py`: `POST /`
All should just return dummy JSON representing their path for now. Let the architecture focus purely on routing.
</action>
<acceptance_criteria>
- `src/faircheck/api/routers/health.py` contains `APIRouter` with `/health`
- `src/faircheck/api/routers/scan.py` contains `POST` referencing `UploadFile`
</acceptance_criteria>
</task>

<task>
<id>04-01-04</id>
<title>Implement FastAPI main App</title>
<read_first>
- src/faircheck/api/routers/health.py
- src/faircheck/api/errors.py
</read_first>
<action>
Create `src/faircheck/api/main.py`.
Initialize `app = FastAPI(title="FairCheck API", version="1.0.0", docs_url="/docs")` (API-08).
Add `CORSMiddleware` with `allow_origins=["*"]`.
Register the custom exception handlers from `errors.py`.
Import and include all routers from `src/faircheck/api/routers/` with the prefix `prefix="/api/v1"`.
</action>
<acceptance_criteria>
- `src/faircheck/api/main.py` contains `app = FastAPI`
- `src/faircheck/api/main.py` contains `CORSMiddleware` setup
- `src/faircheck/api/main.py` contains `app.include_router(..., prefix="/api/v1")`
</acceptance_criteria>
</task>

<task>
<id>04-01-05</id>
<title>Implement programmatic port discovery and server execution</title>
<read_first>
- 04-RESEARCH.md
- src/faircheck/api/main.py
</read_first>
<action>
Create `src/faircheck/api/server.py`.
Implement a `find_free_port()` function that binds to `0` and reads the port.
Implement `def serve():` which calls `find_free_port()`, writes the int port to `~/.faircheck/port` (creating parent dirs as needed), and calls `uvicorn.run("faircheck.api.main:app", host="127.0.0.1", port=port, reload=False)`.
Add a standard `if __name__ == "__main__":` block that calls `serve()`.
</action>
<acceptance_criteria>
- `src/faircheck/api/server.py` contains `uvicorn.run`
- `src/faircheck/api/server.py` writes to `.faircheck/port`
</acceptance_criteria>
</task>

<task>
<id>04-01-06</id>
<title>E2E Routing and Health Tests</title>
<read_first>
- src/faircheck/api/main.py
- src/faircheck/api/server.py
</read_first>
<action>
Create `tests/api/test_health.py` using `fastapi.testclient.TestClient`.
Write a test asserting `client.get("/api/v1/health")` returns 200 `{"status": "ok"}`.
Write a test asserting that querying an invalid route generates a valid RFC 7807 response `{"type": ..., "status": 404, ...}` instead of standard `{detail: "Not Found"}`.
</action>
<acceptance_criteria>
- `tests/api/test_health.py` exits 0 when tested via `uv run pytest tests/api/test_health.py`
</acceptance_criteria>
</task>

<verification>
<must_haves>
- `cat ~/.faircheck/port` contains an integer port output by execution.
- `uv run pytest tests/api/` passes.
- Pydantic models validate input natively over API.
</must_haves>
</verification>

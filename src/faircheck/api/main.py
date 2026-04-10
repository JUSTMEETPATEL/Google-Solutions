"""FairCheck API — FastAPI application entry point.

Mounts all routers under ``/api/v1``, configures open CORS (D-06),
and registers RFC 7807 structured error handlers (D-05).
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from faircheck.api.errors import http_exception_handler, validation_exception_handler
from faircheck.api.routers import health, mitigate, oversight, reports, scan, sessions

app = FastAPI(
    title="FairCheck API",
    description="AI Bias Detection & Fairness Platform — REST API",
    version="1.0.0",
    docs_url="/docs",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # D-06: local-only tool, open CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers (RFC 7807)
# ---------------------------------------------------------------------------

app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Routers — all under /api/v1 (D-02)
# ---------------------------------------------------------------------------

_API_PREFIX = "/api/v1"

app.include_router(health.router, prefix=_API_PREFIX)
app.include_router(scan.router, prefix=_API_PREFIX)
app.include_router(sessions.router, prefix=_API_PREFIX)
app.include_router(mitigate.router, prefix=_API_PREFIX)
app.include_router(reports.router, prefix=_API_PREFIX)
app.include_router(oversight.router, prefix=_API_PREFIX)

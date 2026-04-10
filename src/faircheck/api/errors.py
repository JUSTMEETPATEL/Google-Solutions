"""RFC 7807 Problem Details error handling for the FairCheck API.

Provides structured, machine-readable error responses that are easy
for both the TUI (ink) and Web UI (Vite) clients to parse reliably.

See: https://www.rfc-editor.org/rfc/rfc7807
"""

from __future__ import annotations

from typing import Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details schema."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Override default Starlette HTTP exception handler with RFC 7807."""
    body = ProblemDetails(
        type=f"https://faircheck.dev/errors/{exc.status_code}",
        title=_status_phrase(exc.status_code),
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Override default FastAPI validation exception handler with RFC 7807."""
    errors = exc.errors()
    detail = "; ".join(
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
    )
    body = ProblemDetails(
        type="https://faircheck.dev/errors/validation",
        title="Validation Error",
        status=422,
        detail=detail,
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=422,
        content=body.model_dump(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PHRASES: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    500: "Internal Server Error",
}


def _status_phrase(code: int) -> str:
    return _PHRASES.get(code, "Error")

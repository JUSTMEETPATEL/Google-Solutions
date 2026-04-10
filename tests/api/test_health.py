"""End-to-end tests for the FairCheck API health and error handling.

Tests verify:
  1. GET /api/v1/health returns 200 {"status": "ok"}
  2. Requesting an invalid route returns RFC 7807 structured 404
  3. All router prefixes respond (smoke test)
"""

from fastapi.testclient import TestClient

from faircheck.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


def test_health_returns_ok():
    """GET /api/v1/health should return 200 with {"status": "ok"}."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# RFC 7807 error formatting
# ---------------------------------------------------------------------------


def test_not_found_returns_rfc7807():
    """Requesting a non-existent route should return RFC 7807 JSON, not the
    default FastAPI {"detail": "Not Found"} format."""
    response = client.get("/api/v1/this-does-not-exist")
    assert response.status_code == 404
    body = response.json()
    # RFC 7807 mandatory fields
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert body["status"] == 404
    assert "detail" in body
    assert "instance" in body


# ---------------------------------------------------------------------------
# Router smoke tests — verify each prefix is reachable
# ---------------------------------------------------------------------------


def test_sessions_list_returns_200():
    """GET /api/v1/sessions/ should return 200 (empty list stub)."""
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    assert "sessions" in response.json()


def test_sessions_detail_returns_404():
    """GET /api/v1/sessions/{id} should return 404 (no persistence yet)."""
    response = client.get("/api/v1/sessions/nonexistent")
    assert response.status_code == 404


def test_mitigate_returns_200():
    """POST /api/v1/mitigate/ should return 200 (stub)."""
    response = client.post("/api/v1/mitigate/")
    assert response.status_code == 200


def test_reports_returns_200():
    """POST /api/v1/reports/ should return 200 (stub)."""
    response = client.post("/api/v1/reports/")
    assert response.status_code == 200


def test_oversight_returns_200():
    """POST /api/v1/oversight/ should return 200 (stub)."""
    response = client.post("/api/v1/oversight/")
    assert response.status_code == 200

"""Full integration test: scan + sessions + mitigate + drift."""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:8000/api/v1"
SAMPLES = Path(__file__).parent.parent / "samples"


def test_scan():
    """Test the scan endpoint with the hiring sample."""
    model_path = SAMPLES / "hiring_model.pkl"
    dataset_path = SAMPLES / "hiring_data.csv"

    if not model_path.exists() or not dataset_path.exists():
        print("[SKIP] Sample files not found. Run generate_all_samples.py first.")
        return None

    # Multipart form upload
    import io
    boundary = "----FairCheckTestBoundary"
    body = io.BytesIO()

    for fieldname, filepath in [("model", model_path), ("dataset", dataset_path)]:
        body.write(f"--{boundary}\r\n".encode())
        body.write(
            f'Content-Disposition: form-data; name="{fieldname}"; filename="{filepath.name}"\r\n'.encode()
        )
        body.write(b"Content-Type: application/octet-stream\r\n\r\n")
        body.write(filepath.read_bytes())
        body.write(b"\r\n")

    body.write(f"--{boundary}--\r\n".encode())
    data = body.getvalue()

    req = urllib.request.Request(
        f"{BASE}/scan/",
        data=data,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[FAIL] Scan failed: {e.code} - {error_body}")
        return None

    session_id = result.get("session_id")
    print(f"  [PASS] Scan completed - session: {session_id}")
    print(f"    Status: {result.get('status')}")
    print(f"    Risk: {result.get('analysis_results', {}).get('overall_risk_level')}")
    print(f"    Explanations: {len(result.get('explanations', {}))} attributes")
    print(f"    Intersectional: {'yes' if result.get('intersectional_analysis') else 'no'}")
    print(f"    Confidence Intervals: {'yes' if result.get('confidence_intervals') else 'no'}")
    print(f"    Feature Attribution: {'yes' if result.get('feature_attribution') else 'no'}")
    print(f"    Recommendations: {len(result.get('recommendations', []))}")

    return session_id


def test_session_persistence(session_id):
    """Test that the scan was persisted to DB."""
    resp = urllib.request.urlopen(f"{BASE}/sessions/")
    sessions = json.loads(resp.read())
    assert len(sessions["sessions"]) > 0, "No sessions found!"
    found = any(s["id"] == session_id for s in sessions["sessions"])
    assert found, f"Session {session_id} not in list!"
    print(f"  [PASS] Session persisted - {len(sessions['sessions'])} total")

    # Fetch full session detail
    resp = urllib.request.urlopen(f"{BASE}/sessions/{session_id}")
    detail = json.loads(resp.read())
    assert "analysis_results" in detail
    assert "explanations" in detail
    assert "recommendations" in detail
    print(f"  [PASS] Session detail retrieved with all analysis data")
    return detail


def test_mitigation(session_id):
    """Test mitigation recommendations and application."""
    # First: get recommendations only
    data = json.dumps({"session_id": session_id}).encode()
    req = urllib.request.Request(
        f"{BASE}/mitigate/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    assert result["status"] == "recommendations"
    recs = result["recommendations"]
    print(f"  [PASS] Mitigation recommendations: {len(recs)} strategies")

    if recs and recs[0]["algorithm"] != "none":
        # Apply the top recommendation
        algo = recs[0]["algorithm"]
        data2 = json.dumps({"session_id": session_id, "algorithm": algo}).encode()
        req2 = urllib.request.Request(
            f"{BASE}/mitigate/",
            data=data2,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp2 = urllib.request.urlopen(req2)
        result2 = json.loads(resp2.read())
        assert result2["status"] == "applied"
        print(f"  [PASS] Mitigation applied: {algo}")


def test_oversight(session_id):
    """Test oversight submission."""
    data = json.dumps({
        "session_id": session_id,
        "reviewer": "Test Reviewer",
        "decision": "approved",
        "notes": "Integration test"
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/oversight/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    assert result["success"] is True
    print(f"  [PASS] Oversight submitted: approved")


if __name__ == "__main__":
    print("\n=== FairCheck Integration Tests ===\n")

    sid = test_scan()
    if sid is None:
        print("\n[SKIP] Cannot continue without scan results")
        sys.exit(1)

    test_session_persistence(sid)
    test_mitigation(sid)
    test_oversight(sid)

    print("\n=== All integration tests passed! ===\n")

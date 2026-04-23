"""Quick test: POST to /api/v1/scan/ with sample files."""

import json
import uuid
import urllib.request
import urllib.error


def build_multipart(files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    """Build multipart/form-data body from {field: (filename, data, mime)}."""
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for field, (filename, data, mime) in files.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{field}"; '
            f'filename="{filename}"\r\n'.encode()
        )
        parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
        parts.append(data)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


with open("samples/hiring_model.pkl", "rb") as f:
    model_data = f.read()
with open("samples/hiring_data.csv", "rb") as f:
    dataset_data = f.read()

body, boundary = build_multipart({
    "model": ("hiring_model.pkl", model_data, "application/octet-stream"),
    "dataset": ("hiring_data.csv", dataset_data, "text/csv"),
})

req = urllib.request.Request(
    "http://127.0.0.1:56821/api/v1/scan/",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

try:
    resp = urllib.request.urlopen(req, timeout=60)
    data = json.loads(resp.read())
    print("OK Status: 200")
    print("Session ID:", data.get("session_id", "N/A"))
    print("Risk Level:", data.get("analysis_results", {}).get("overall_risk_level", "N/A"))
    print("Protected:", data.get("analysis_results", {}).get("protected_attributes", []))
    # Show metric summary
    results = data.get("analysis_results", {}).get("results", {})
    for attr, attr_data in results.items():
        print(f"\n--- {attr} ---")
        for metric_name, metric_data in attr_data.get("metrics", {}).items():
            status = metric_data.get("status", "?")
            value = metric_data.get("value", "?")
            print(f"  {metric_name}: {value:.4f} [{status}]")
except urllib.error.HTTPError as e:
    print(f"FAIL Error {e.code}:", e.read().decode()[:800])

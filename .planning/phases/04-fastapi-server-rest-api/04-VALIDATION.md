---
phase: 04
slug: fastapi-server-rest-api
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-10
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `uv run pytest tests/api/test_xyz.py` |
| **Full suite command** | `uv run pytest tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/api/` matching the modified components.
- **After every plan wave:** Run `uv run pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | API-01 | — | N/A | setup | `uv sync` | ✅ | ⬜ pending |
| 04-01-02 | 02 | 1 | API-05 | — | N/A | unit | `uv run pytest tests/api/test_health.py` | ❌ W0 | ⬜ pending |
| 04-01-03 | 02 | 1 | API-02 | — | N/A | unit | `uv run pytest tests/api/test_scan.py` | ❌ W0 | ⬜ pending |
| 04-01-04 | 02 | 1 | API-03 | — | N/A | unit | `uv run pytest tests/api/test_sessions.py` | ❌ W0 | ⬜ pending |
| 04-01-05 | 02 | 1 | D-05 | — | N/A | unit | `uv run pytest tests/api/test_errors.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/api/__init__.py` — Package setup
- [ ] `tests/api/test_health.py` — Health endpoint test stubs
- [ ] `tests/api/test_scan.py` — Scan endpoint test stubs
- [ ] `tests/api/test_sessions.py` — Session endpoint test stubs
- [ ] `tests/api/test_errors.py` — RFC 7807 Error test stubs

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Port generation | API-01 | Requires finding an open port outside of test logic | Ensure `~/.faircheck/port` generates via `python -m faircheck.api.server` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

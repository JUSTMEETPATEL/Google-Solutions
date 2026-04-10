---
phase: 05
slug: session-persistence-sqlite
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `pytest tests/api/test_sessions.py -x` |
| **Full suite command** | `pytest tests/api/test_sessions.py` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick test or syntax check
- **After every plan wave:** Run full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | SESS-01 | — | N/A | unit | `pytest tests/api/test_sessions_db.py` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | SESS-02, SESS-05 | — | N/A | unit | `pytest tests/api/test_sessions_schema.py` | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | SESS-04 | — | N/A | unit | `pytest tests/api/test_sessions_wal.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/api/test_sessions_db.py` — stubs for DB initialization and WAL checking
- [ ] `tests/api/test_sessions_schema.py` — stubs for schema and JSON columns verification

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Alembic migrates properly | SESS-01 | Setup/teardown requires CLI | Run `alembic init` then `alembic revision -m "init"` manually. |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

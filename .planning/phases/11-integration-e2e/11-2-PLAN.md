---
phase: 11
plan: 2
title: "TUI→Web Handoff & E2E Integration Tests"
wave: 2
depends_on: [11-1]
files_modified:
  - tui/src/commands/ScanView.tsx
  - tui/src/api.ts
  - tests/integration/test_e2e.py
requirements: [INT-01, INT-05]
autonomous: true
---

# Plan 11-2: TUI→Web Handoff & E2E Integration Tests

<objective>
Wire the TUI [W] hotkey to spawn/discover the Vite web server with the session pre-loaded,
and create end-to-end integration tests validating the full pipeline.
</objective>

## Tasks

<task id="11-2-1" title="Update TUI [W] hotkey for proper handoff">
<action>
Update `tui/src/commands/ScanView.tsx`:
- [W] reads port from `~/.faircheck/port`
- Polls health endpoint before opening browser
- Opens `http://localhost:{port}?session={sessionId}` so session is pre-loaded

Update `tui/src/api.ts`:
- Add `pollHealth(timeout: number)` — polls until API responds or timeout
</action>
</task>

<task id="11-2-2" title="Create E2E integration tests">
<action>
Create `tests/integration/test_e2e.py`:

1. **Full pipeline test (INT-05)**: Creates synthetic model+dataset → runs
   BiasAnalyzer → applies mitigation → generates report → verifies PDF exists
2. **Port file test**: Writes port → reads back → matches
3. **Report with regulation test**: Full pipeline with `regulation="eu_ai_act"` 
   → PDF contains Article references
4. **Session persistence test**: Creates session → fetches by ID → data matches

These are Python-level integration tests that exercise the full engine pipeline
without needing a running server.
</action>

<acceptance_criteria>
- All integration tests pass
- Full pipeline produces valid PDF output
- No regressions
</acceptance_criteria>
</task>

<verification>
- `pytest tests/integration/ -v` — all tests pass
- `pytest tests/ -q` — no regressions
- `tsc --noEmit` in tui/ — 0 errors
</verification>

---
phase: 6
slug: tui-interface-ink
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-11
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest |
| **Config file** | tui/vitest.config.ts |
| **Quick run command** | `cd tui && npm run test` |
| **Full suite command** | `cd tui && npm run test` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd tui && npm run test`
- **After every plan wave:** Run `cd tui && npm run test`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | TUI-01 | — | N/A | setup | `cd tui && npm run build` | ✅ | ⬜ pending |
| 06-01-02 | 01 | 1 | TUI-01 | — | N/A | unit | `cd tui && npm run test orchestrator` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | TUI-01 | — | N/A | unit | `cd tui && npm run test api` | ❌ W0 | ⬜ pending |
| 06-01-04 | 01 | 1 | TUI-02/03/07 | — | N/A | unit | `cd tui && npm run test components` | ❌ W0 | ⬜ pending |
| 06-01-05 | 01 | 1 | TUI-04/05/06 | — | N/A | unit | `cd tui && npm run test app` | ❌ W0 | ⬜ pending |
| 06-01-06 | 01 | 1 | TUI-01 | — | N/A | unit | `cd tui && npm run test cli` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tui/package.json` — vitest installed
- [ ] `tui/tests/orchestrator.test.ts` — stubs for orchestrator
- [ ] `tui/tests/api.test.ts` — stubs for api
- [ ] `tui/tests/app.test.tsx` — stubs for the App interactions

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual colored table rendering | TUI-02 | ANSI coloring and absolute positioning must be verified by eye. | Run `node tui/dist/cli.js scan model.pkl --dataset train.csv` and observe colors. |
| [W] / [R] Keyboard interaction | TUI-04, TUI-05 | Interactive keypresses are difficult to mock exactly as user presses. | While TUI is running, press 'w', press 'r', ensure outputs occur. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

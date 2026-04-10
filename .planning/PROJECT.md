# FairCheck — AI Bias Detection & Fairness Platform

## What This Is

An end-to-end AI bias detection and fairness platform that bridges the gap between data science tooling and compliance-ready governance. It delivers a complete pipeline — from raw model ingestion to regulation-ready audit reports — through two interfaces sharing one engine: a TUI for developers (SSH-compatible, scriptable) and a Vite + React web app for compliance teams. Local-first: no model data ever leaves the machine.

## Core Value

Produce regulation-ready AI bias audit reports in under 20 minutes — from model upload to downloadable PDF — that a compliance officer can sign off on without needing to understand the underlying data science.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — ship to validate)

### Active

- [ ] Python engine wrapping AIF360/Fairlearn with local FastAPI
- [ ] Model ingestion for .pkl, .joblib, .onnx formats
- [ ] CSV, Parquet, JSON dataset support
- [ ] Protected attribute auto-detection with confidence scoring
- [ ] 6 core fairness metrics: demographic parity, equalized odds, disparate impact ratio, predictive parity, calibration by group, individual fairness
- [ ] Pre/in/post-processing mitigation algorithms (reweighing, adversarial debiasing, calibrated equalized odds, etc.)
- [ ] Session persistence via local SQLite store
- [ ] TUI (`ink`) with `faircheck scan` command, metric summary, CI mode, [W]/[R] hotkeys
- [ ] Vite + React web app with bias dashboard, regulation selector, risk score card, report export
- [ ] Human oversight log for audit trail (reviewer name, date, decision, sign-off)
- [ ] EU AI Act report template (Articles 9, 10, 13, 14, 17)
- [ ] PDF/Markdown/DOCX report generation via Jinja2 + WeasyPrint
- [ ] Local REST API (FastAPI) for engine ↔ UI communication

### Out of Scope

- Cloud/SaaS hosting — local-first for v1; Next.js migration deferred to SaaS pivot
- India DPDPA report templates — Phase 3 (Month 10–18), not v1
- Real-time collaborative editing — single-user compliance tool
- OAuth/SSO — not needed for local-first tool
- Mobile app — desktop/terminal only
- Multi-tenant architecture — single user, single machine
- Slack/webhook notifications — P2 feature
- Video walkthrough embedding — P2 feature

## Context

- **Regulatory forcing function:** EU AI Act high-risk system enforcement begins August 2026. Fines up to €35M or 7% global turnover. This is the primary go-to-market deadline.
- **Competitive gap:** IBM AIF360, Microsoft Fairlearn, Google What-If Tool all provide algorithms but none produce compliance-ready reports. No end-to-end pipeline exists.
- **Architecture:** Python engine (core) ↔ local REST API ↔ Node.js interfaces (TUI via ink, Web via Vite+React). Shared session state via SQLite at `~/.faircheck/sessions.db`.
- **Go-to-market:** Phase 1 OSS (developer trust via GitHub) → Phase 2 paid web compliance layer → Phase 3 India DPDPA expansion.
- **Target users:** ML engineers ("Terminal Maya") via TUI, compliance officers ("Audit Priya") via web app, CTOs ("Strategic Sam") via portfolio dashboards.

## Constraints

- **Tech Stack (Engine)**: Python 3.11+, AIF360 + Fairlearn (wrapped), FastAPI, SQLite via SQLAlchemy, Jinja2 + WeasyPrint — inherits existing ecosystem
- **Tech Stack (TUI)**: Node.js, `ink` (React-in-terminal) — chosen for component reuse with web layer
- **Tech Stack (Web)**: Vite 5+, React 18, Tailwind CSS + shadcn/ui, Recharts, Zustand, TanStack Query — no SSR needed
- **Local-first**: No model data transmitted to cloud. Engine runs entirely on-device.
- **Timeline**: M0–M5 (Months 1–6) for OSS launch; M6 (Month 8) paid tier; hard deadline August 2026
- **Licensing**: Engine is MIT-licensed OSS; compliance web layer is paid add-on

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vite over Next.js for v1 web app | No SSR needed; faster HMR; simpler config for local-only tool | — Pending |
| `ink` for TUI framework | React component model enables code reuse with web layer | — Pending |
| Python for engine, Node.js for UIs | Python inherits AIF360/Fairlearn ecosystem; Node.js for modern UI tooling | — Pending |
| Local SQLite for session state | Zero-config, file-based, portable; no DB server to manage | — Pending |
| MIT license for engine | Builds developer trust (IBM AIF360 playbook); paid compliance layer for revenue | — Pending |
| FastAPI for local IPC | Async, auto-docs, lightweight; both UIs communicate over localhost REST | — Pending |
| Jinja2 + WeasyPrint for reports | PDF generation without heavy dependencies; template-driven for regulation flexibility | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after initialization*

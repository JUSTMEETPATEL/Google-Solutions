# Research Summary: AI Bias Detection & Fairness Platform

## Stack Verdict

**Engine:** Python 3.11+ with Fairlearn (primary) + AIF360 (extended algorithms), FastAPI for local REST API, SQLite via SQLAlchemy for sessions, Jinja2 + WeasyPrint for PDF reports.

**TUI:** Node.js with ink (React-in-terminal), commander.js for CLI parsing.

**Web:** Vite 6 + React 19 + TypeScript, Tailwind CSS + shadcn/ui, Recharts for charts, Zustand for state, TanStack Query for API calls.

**Confidence:** High. This stack aligns with the PRD's decisions and is validated by current ecosystem analysis. No controversial choices.

## Table Stakes Features

1. Model ingestion (pkl, joblib, ONNX) + dataset handling (CSV, Parquet, JSON)
2. Core fairness metrics (demographic parity, equalized odds, disparate impact, predictive parity)
3. Pass/fail/warning status per metric with configurable thresholds
4. Per-group demographic breakdown
5. PDF report generation with metric tables and charts
6. CLI `scan` command with CI mode (exit code 1 on failure)
7. Web dashboard with upload, charts, and download
8. Session persistence for audit history

## Key Differentiators

1. **Regulation-mapped output** — EU AI Act article-by-article template coverage (NO competitor does this)
2. **Human oversight log** — EU AI Act Art. 14 compliance with reviewer sign-off
3. **Dual interface** — TUI for developers, web for compliance officers, shared session state
4. **End-to-end pipeline** — ingestion → analysis → mitigation → report in one tool
5. **Local-first** — sensitive model data never leaves the machine

## Watch Out For

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Fairness metrics are mutually exclusive — can't satisfy all | Critical | Domain-specific guidance on metric selection; don't present as "pass all" |
| WeasyPrint system dependencies vary by OS | High | Provide Docker image + fallback to Markdown-only reports |
| Protected attribute auto-detection false positives | Critical | Always require human confirmation; show confidence scores |
| Regulation template legal accuracy | Critical | Label as "guidance," add disclaimers, recommend legal review |
| Data leakage in mitigation pipeline | Critical | Enforce train/test split; apply mitigation only to training data |
| Treating fairness as checkbox exercise | Critical | Add contextual warnings; reports say "analysis" not "certification" |

## Architecture Highlights

- Engine is a library first, API second — importable Python modules, not just REST endpoints
- FastAPI is a thin adapter (~200 LOC glue) — all intelligence in engine
- SQLite WAL mode prevents write contention between TUI and Web
- TUI→Web handoff via session_id in URL query param
- Random port for FastAPI with PID file for process management

## Build Order (Recommended)

1. Engine Core (ingestion + analysis algorithms)
2. FastAPI Server (thin REST adapter)
3. Session Store (SQLite persistence)
4. TUI Interface (first user-facing surface)
5. Report Builder (core differentiator — PDF/DOCX)
6. Web Dashboard (compliance officer interface)
7. Mitigation Pipeline (optional bias correction)
8. Human Oversight (audit trail)
9. Regulation Templates (EU AI Act mapping)
10. Integration Testing (TUI↔Web handoff, CI mode, E2E)

---
*Synthesized: 2026-04-10*

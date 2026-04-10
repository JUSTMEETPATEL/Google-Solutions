# Architecture Research: AI Bias Detection & Fairness Platform

## Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                          │
│                                                              │
│  ┌─────────────────────┐    ┌───────────────────────────┐   │
│  │   TUI (ink / Node)  │    │  Web App (Vite + React)   │   │
│  │                     │    │                           │   │
│  │  • faircheck scan   │    │  • Drag-drop upload       │   │
│  │  • Metric table     │    │  • Bias dashboard         │   │
│  │  • CI mode          │◄──►│  • Report export          │   │
│  │  • [W] web launch   │    │  • Human oversight log    │   │
│  │  • [R] report gen   │    │  • Regulation selector    │   │
│  └────────┬────────────┘    └──────────┬────────────────┘   │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │ HTTP (localhost)                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│                   ENGINE API LAYER                            │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────────────────┐  │
│  │              FastAPI (localhost:PORT)                   │  │
│  │                                                       │  │
│  │  POST /api/scan          — start bias analysis        │  │
│  │  GET  /api/sessions      — list past sessions         │  │
│  │  GET  /api/sessions/{id} — get session detail         │  │
│  │  POST /api/mitigate      — apply mitigation           │  │
│  │  POST /api/report        — generate report            │  │
│  │  GET  /api/metrics       — available metrics config    │  │
│  │  POST /api/oversight     — record human oversight     │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│                   CORE ENGINE                                │
│                        │                                     │
│  ┌─────────────────────▼─────────────────────────────────┐  │
│  │              Pipeline Orchestrator                     │  │
│  │                                                       │  │
│  │  1. Ingestion  →  2. Analysis  →  3. Mitigation       │  │
│  │                                    (optional)          │  │
│  │                         ↓                              │  │
│  │              4. Report Generation                      │  │
│  └─────────┬─────────┬───────────┬───────────┬───────────┘  │
│            │         │           │           │               │
│  ┌─────────▼───┐ ┌───▼──────┐ ┌─▼─────────┐ ┌▼────────────┐│
│  │  Ingestion  │ │ Analysis │ │ Mitigation│ │   Report    ││
│  │  Module     │ │ Module   │ │ Module    │ │   Builder   ││
│  │            │ │          │ │           │ │             ││
│  │ • pkl      │ │ • dem.   │ │ • reweigh │ │ • Jinja2    ││
│  │ • joblib   │ │   parity │ │ • adv.    │ │ • WeasyPrint││
│  │ • onnx     │ │ • eq.odds│ │   debias  │ │ • python-   ││
│  │ • csv      │ │ • disp.  │ │ • calib.  │ │   docx      ││
│  │ • parquet  │ │   impact │ │   eq.odds │ │ • Templates ││
│  │ • json     │ │ • pred.  │ │ • ROC     │ │   (EU, IN)  ││
│  │            │ │   parity │ │           │ │             ││
│  └─────────────┘ └──────────┘ └───────────┘ └─────────────┘│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Session Store (SQLite)                     │  │
│  │              ~/.faircheck/sessions.db                   │  │
│  │                                                       │  │
│  │  sessions | scan_results | mitigations | oversight     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Primary Flow: Scan → Report

```
1. User provides: model file + dataset file + config
2. Ingestion: load model, load dataset, infer types, detect protected attributes
3. User confirms: protected attributes selection
4. Analysis: compute all selected fairness metrics per protected attribute
5. Results: structured JSON with per-metric, per-group results
6. (Optional) Mitigation: apply selected algorithm, re-compute metrics
7. Report: populate regulation template with results, generate PDF/MD/DOCX
8. Session: persist all above to SQLite for retrieval
```

### TUI → Web Handoff

```
1. TUI runs scan → results persisted to SQLite (session_id)
2. User presses [W]
3. TUI spawns: `npx vite` on random port
4. TUI opens browser: `http://localhost:{port}?session={session_id}`
5. Web app reads session from SQLite → renders dashboard
6. Same session, different view
```

## Component Boundaries

| Component | Owns | Talks To | Language |
|-----------|------|----------|----------|
| Engine Core | Bias algorithms, metrics, models | Nothing (library) | Python |
| FastAPI Server | REST API, request validation, session management | Engine Core, SQLite | Python |
| TUI | Terminal UI, CLI parsing, hotkeys | FastAPI (HTTP), Vite (spawn) | Node.js |
| Web App | Browser UI, charts, forms | FastAPI (HTTP), SQLite (read) | TypeScript |
| Report Builder | Templates, PDF/DOCX generation | Engine Core results | Python |
| Session Store | Data persistence, history | All (shared resource) | SQLite |

## Suggested Build Order

Based on dependency analysis:

```
Phase 1: Engine Core (ingestion + analysis) — foundation, no UI dependency
Phase 2: FastAPI Server — wraps engine for IPC
Phase 3: Session Store — enables persistence
Phase 4: TUI — first user-facing interface
Phase 5: Report Builder — core differentiator
Phase 6: Web App — second interface, richer UX
Phase 7: Mitigation — optional pipeline stage
Phase 8: Human Oversight — compliance feature
Phase 9: Regulation Templates — EU AI Act mapping
Phase 10: Integration — TUI↔Web handoff, CI mode
```

## Key Architectural Decisions

1. **Engine as library, not service:** Core bias algorithms should be importable Python modules, not only accessible via API. This enables testing, notebook use, and CI integration without FastAPI.

2. **FastAPI as thin adapter:** The API layer should be ~200 lines of glue code, not business logic. All intelligence lives in the engine.

3. **SQLite as shared state:** Both TUI and Web read/write the same `sessions.db`. No sync protocol needed — SQLite handles concurrent reads, and single-user means no write contention.

4. **Random port for FastAPI:** Avoid port conflicts. Write port to `~/.faircheck/port` for TUI/Web to discover.

5. **Web app is static:** Vite serves static files; all data comes from FastAPI REST calls. No server-side rendering needed.

---
*Researched: 2026-04-10*

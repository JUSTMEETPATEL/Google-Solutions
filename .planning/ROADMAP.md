# Roadmap: FairCheck — AI Bias Detection & Fairness Platform

**Version:** v1.0
**Created:** 2026-04-10
**Granularity:** Fine
**Total Phases:** 11
**Total Requirements:** 72

## Milestone 1: v1.0 — OSS Launch

### Phase 1: Engine Foundation & Project Scaffold
**Goal:** Establish the Python project structure, dependency management, and wrapper abstractions around AIF360/Fairlearn.
**Requirements:** ENG-01, ENG-02, ENG-03
**UI hint:** no
**Depends on:** nothing

**Success Criteria:**
1. Python package skeleton builds and passes initial test suite
2. `faircheck.algorithms` wrapper module imports and exposes unified API across AIF360 and Fairlearn
3. Configuration system loads `.faircheckrc` with metric thresholds, protected attributes, and report preferences
4. Upstream library API changes are isolated behind the wrapper — no direct AIF360/Fairlearn imports outside wrapper module

### Phase 2: Model & Dataset Ingestion Pipeline
**Goal:** Build the data-loading layer that accepts model files (.pkl, .joblib, .onnx) and datasets (CSV, Parquet, JSON) with automatic type inference and protected attribute detection.
**Requirements:** ING-01, ING-02, ING-03, ING-04, ING-05, ING-06, ING-07, ING-08, ING-09
**UI hint:** no
**Depends on:** Phase 1

**Success Criteria:**
1. User can load a scikit-learn model from .pkl and a dataset from CSV, and the system returns model predictions on the dataset
2. Column type inference correctly identifies numeric, categorical, and binary columns on a test dataset
3. Protected attribute auto-detection identifies "gender" and "age" columns in a sample dataset with confidence scores ≥ 0.8
4. User can override auto-detected attributes via programmatic API
5. All 3 model formats and 3 dataset formats load without error on representative test files

### Phase 3: Bias Analysis Engine
**Goal:** Implement the 6 core fairness metrics with configurable thresholds, per-group breakdowns, and domain-specific guidance.
**Requirements:** BIAS-01, BIAS-02, BIAS-03, BIAS-04, BIAS-05, BIAS-06, BIAS-07, BIAS-08, BIAS-09
**UI hint:** no
**Depends on:** Phase 2

**Success Criteria:**
1. All 6 fairness metrics compute correctly against known benchmark datasets (compare to raw AIF360/Fairlearn output)
2. Each metric returns pass/fail/warning status against default thresholds
3. Per-group breakdown shows accuracy, precision, recall, F1 for each demographic subgroup
4. Domain guidance returns appropriate metric recommendations for hiring, lending, and healthcare use cases
5. Custom thresholds override defaults when provided via config

### Phase 4: FastAPI Server & REST API
**Goal:** Wrap the engine in a FastAPI server with full REST API for scan, sessions, mitigation, reports, oversight, and health check endpoints.
**Requirements:** API-01, API-02, API-03, API-04, API-05, API-06, API-07, API-08
**UI hint:** no
**Depends on:** Phase 3

**Success Criteria:**
1. FastAPI starts on a random port and writes port to ~/.faircheck/port
2. POST /api/scan accepts a model + dataset upload, runs analysis, and returns structured JSON results
3. GET /api/sessions returns list of past scans; GET /api/sessions/{id} returns full detail
4. GET /api/health returns 200 within 100ms
5. All endpoints have auto-generated Swagger documentation at /docs

### Phase 5: Session Persistence (SQLite)
**Goal:** Implement the local SQLite session store with schema for sessions, scan results, mitigations, and oversight records.
**Requirements:** SESS-01, SESS-02, SESS-03, SESS-04, SESS-05
**UI hint:** no
**Depends on:** Phase 4

**Success Criteria:**
1. Scan results persist to ~/.faircheck/sessions.db and survive server restart
2. Session record includes model metadata, dataset metadata, all metric results, and timestamps
3. Session list returns summary with model name, date, and computed risk level
4. SQLite configured with WAL mode (verified via PRAGMA check)
5. Mitigation history persists: algorithm applied, before metrics, after metrics

### Phase 6: TUI Interface (ink)
**Goal:** Build the terminal interface using ink with scan command, metric table rendering, protected attribute confirmation, session list, CI mode, and [W]/[R] hotkeys.
**Requirements:** TUI-01, TUI-02, TUI-03, TUI-04, TUI-05, TUI-06, TUI-07
**UI hint:** no
**Depends on:** Phase 5

**Success Criteria:**
1. `faircheck scan model.pkl --dataset train.csv` produces a colored terminal table of all metrics with pass/fail/warning
2. Protected attribute detection shows interactive confirmation prompt with confidence scores
3. `--ci` flag exits with code 1 when at least one metric breaches threshold, code 0 when all pass
4. [R] hotkey generates PDF report and saves to current directory
5. Session list shows past 10 scans with model name, date, risk level

### Phase 7: Report Builder (PDF/MD/DOCX)
**Goal:** Implement the template-driven report generation system with Jinja2 templates, WeasyPrint PDF output, Markdown output, and DOCX output including all 9 required report sections.
**Requirements:** RPT-01, RPT-02, RPT-03, RPT-04, RPT-05, RPT-06, RPT-07, RPT-08, RPT-09, RPT-10, RPT-11
**UI hint:** no
**Depends on:** Phase 5

**Success Criteria:**
1. PDF report opens correctly with cover page showing model name, audit date, and regulation standard
2. Executive summary section uses plain language understandable by non-technical stakeholders
3. Demographic breakdown includes charts (bar charts for per-group metrics)
4. All 3 output formats (PDF, Markdown, DOCX) generate without errors from same session data
5. Report includes methodology appendix with raw metric values and computation notes

### Phase 8: Web App (Vite + React Dashboard)
**Goal:** Build the compliance officer-facing web dashboard with Vite + React, including session sidebar, drag-drop upload, bias charts, regulation selector, risk score card, PDF download, and human oversight form.
**Requirements:** WEB-01, WEB-02, WEB-03, WEB-04, WEB-05, WEB-06, WEB-07
**UI hint:** yes
**Depends on:** Phase 5

**Success Criteria:**
1. Web app loads at localhost:5173 and displays session history in sidebar
2. Drag-and-drop upload accepts model + dataset files, triggers scan, and displays results
3. Bias dashboard renders Recharts charts for demographic parity and equalized odds by group
4. Regulation selector filters risk thresholds and report template based on selected framework
5. Human oversight form captures reviewer name, date, and decision, persists to session

### Phase 9: Mitigation Pipeline
**Goal:** Implement the pre/in/post-processing mitigation algorithms with before/after comparison and train/test split enforcement.
**Requirements:** MIT-01, MIT-02, MIT-03, MIT-04, MIT-05, MIT-06, MIT-07, MIT-08
**UI hint:** no
**Depends on:** Phase 3

**Success Criteria:**
1. Reweighing mitigation reduces Demographic Parity Difference on a benchmark dataset
2. Before/after metrics displayed correctly show improvement or trade-off
3. Mitigation is only applied to training data; test set remains untouched
4. At least 3 different mitigation algorithms run without error on the same session
5. Mitigation results persist to session store with full audit trail

### Phase 10: Regulation Templates (EU AI Act)
**Goal:** Create the EU AI Act regulation-mapped report templates with article-by-article cross-referencing, risk classification, and compliance disclaimers.
**Requirements:** REG-01, REG-02, REG-03, REG-04, REG-05, REG-06, REG-07
**UI hint:** no
**Depends on:** Phase 7

**Success Criteria:**
1. EU AI Act report template covers Articles 9, 10, 13, 14, and 17 with specific section content
2. Each report section cross-references the specific EU AI Act article it satisfies
3. Human oversight section links to recorded oversight decisions from WEB-07
4. Disclaimer clearly states report is guidance, not legal certification
5. Risk classification (High/Medium/Low) is automatically derived from metric ensemble

### Phase 11: Integration & E2E Testing
**Goal:** Wire together TUI→Web handoff, port discovery, health check polling, PID management, and validate the full end-to-end flow across both interfaces.
**Requirements:** INT-01, INT-02, INT-03, INT-04, INT-05
**UI hint:** no
**Depends on:** Phase 6, Phase 8

**Success Criteria:**
1. TUI [W] hotkey spawns Vite server and opens browser with current session pre-loaded
2. Port discovery file is atomically written; TUI/Web read correct port
3. Health check polling prevents browser opening before API is ready
4. PID file prevents duplicate FastAPI instances
5. Full E2E: upload model via TUI → view results in web → download PDF report — all from same session

---
*Roadmap created: 2026-04-10*
*Last updated: 2026-04-10 after initial creation*

# Requirements: FairCheck — AI Bias Detection & Fairness Platform

**Defined:** 2026-04-10
**Core Value:** Produce regulation-ready AI bias audit reports in under 20 minutes — from model upload to downloadable PDF — that a compliance officer can sign off on without needing to understand the underlying data science.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Engine Foundation

- [ ] **ENG-01**: Engine scaffold with Python 3.11+ project structure, dependency management (pyproject.toml), and test infrastructure
- [ ] **ENG-02**: Abstract wrapper layer around AIF360 and Fairlearn that isolates upstream API changes
- [ ] **ENG-03**: Configuration system for metric thresholds, protected attributes, and report preferences (.faircheckrc)

### Model Ingestion

- [ ] **ING-01**: User can load scikit-learn models from .pkl files
- [ ] **ING-02**: User can load models from .joblib files
- [ ] **ING-03**: User can load models from .onnx files via ONNX Runtime
- [ ] **ING-04**: User can load datasets from CSV files
- [ ] **ING-05**: User can load datasets from Parquet files
- [ ] **ING-06**: User can load datasets from JSON files
- [ ] **ING-07**: System automatically infers column types (numeric, categorical, binary)
- [ ] **ING-08**: System auto-detects likely protected attributes (gender, race, age columns) with confidence scores
- [ ] **ING-09**: User can confirm or override auto-detected protected attributes

### Bias Analysis

- [ ] **BIAS-01**: System computes Demographic Parity Difference per protected group (default threshold ≤ 0.10)
- [ ] **BIAS-02**: System computes Equalized Odds Difference per protected group (default threshold ≤ 0.10)
- [ ] **BIAS-03**: System computes Disparate Impact Ratio per protected group (default threshold ≥ 0.80)
- [ ] **BIAS-04**: System computes Predictive Parity per protected group (default threshold ≤ 0.10)
- [ ] **BIAS-05**: System computes Calibration by Group per protected group (default threshold ≤ 0.05)
- [ ] **BIAS-06**: System computes Individual Fairness (cosine-based) with configurable threshold
- [ ] **BIAS-07**: Each metric displays pass/fail/warning status against configured thresholds
- [ ] **BIAS-08**: System provides per-group performance breakdown (accuracy, precision, recall, F1 per demographic)
- [ ] **BIAS-09**: System provides domain-specific guidance on metric selection (hiring, lending, healthcare)

### API Layer

- [ ] **API-01**: FastAPI server starts on random available port with port discovery file (~/.faircheck/port)
- [ ] **API-02**: POST /api/scan endpoint accepts model file + dataset + config, returns analysis results
- [ ] **API-03**: GET /api/sessions endpoint lists past scan sessions
- [ ] **API-04**: GET /api/sessions/{id} endpoint returns full session detail with metrics
- [ ] **API-05**: POST /api/mitigate endpoint accepts session_id + algorithm, returns before/after metrics
- [ ] **API-06**: POST /api/report endpoint generates report for a session
- [ ] **API-07**: GET /api/health endpoint returns server status (for TUI readiness polling)
- [ ] **API-08**: POST /api/oversight endpoint records human oversight decision for a session

### Session Persistence

- [ ] **SESS-01**: All scan results persist to local SQLite store at ~/.faircheck/sessions.db
- [ ] **SESS-02**: Session includes: model metadata, dataset metadata, metric results, timestamps
- [ ] **SESS-03**: User can list past sessions with summary (model name, date, risk level)
- [ ] **SESS-04**: SQLite runs in WAL mode to prevent write contention between TUI and Web
- [ ] **SESS-05**: Session data includes mitigation history (algorithm applied, before/after metrics)

### TUI Interface

- [ ] **TUI-01**: `faircheck scan model.pkl --dataset train.csv` command runs full bias analysis pipeline
- [ ] **TUI-02**: Terminal-rendered table of key fairness metrics with pass/fail/warning status and color coding
- [ ] **TUI-03**: Protected attribute auto-detection with interactive confirmation prompt
- [ ] **TUI-04**: `[W]` hotkey starts Vite web server and opens localhost in default browser with current session pre-loaded
- [ ] **TUI-05**: `[R]` hotkey generates PDF/MD report for current session
- [ ] **TUI-06**: `--ci` flag exits with code 1 if any fairness threshold is breached (for GitHub Actions / pre-commit hooks)
- [ ] **TUI-07**: Session list view showing past scans with model name, date, and risk level

### Web App

- [ ] **WEB-01**: Session loader reads from local SQLite and shows scan history in sidebar
- [ ] **WEB-02**: Model + dataset upload via drag-and-drop (files stay local, no network requests)
- [ ] **WEB-03**: Bias dashboard with visual charts: demographic parity, equalized odds, disparate impact ratio by group
- [ ] **WEB-04**: Regulation selector dropdown: EU AI Act (High Risk), EU AI Act (Limited Risk), India DPDPA, Custom
- [ ] **WEB-05**: Risk score card showing overall risk level (High/Medium/Low) with per-metric breakdowns
- [ ] **WEB-06**: One-click PDF export of the compliance report
- [ ] **WEB-07**: Human oversight log form: reviewer name, date, decision, sign-off for audit trail

### Report Generation

- [ ] **RPT-01**: Report includes cover page with model name, version, audit date, reviewer, regulation standard
- [ ] **RPT-02**: Report includes executive summary in plain language (suitable for non-technical stakeholders)
- [ ] **RPT-03**: Report includes model card: training data description, intended use, known limitations
- [ ] **RPT-04**: Report includes bias analysis results table with threshold, actual value, and status per metric
- [ ] **RPT-05**: Report includes demographic breakdown charts (per-group performance)
- [ ] **RPT-06**: Report includes mitigation applied section: algorithm used, before/after metric comparison
- [ ] **RPT-07**: Report includes human oversight record: reviewer name, date, decision, signature field
- [ ] **RPT-08**: Report includes appendix with raw metric data and methodology notes
- [ ] **RPT-09**: PDF output via Jinja2 + WeasyPrint templates
- [ ] **RPT-10**: Markdown output as lightweight alternative
- [ ] **RPT-11**: DOCX output via python-docx for Word editing

### Regulation Mapping

- [ ] **REG-01**: EU AI Act Article 9 mapping — risk management system documentation in report
- [ ] **REG-02**: EU AI Act Article 10 mapping — training data governance and bias monitoring section
- [ ] **REG-03**: EU AI Act Article 13 mapping — transparency and information provision section
- [ ] **REG-04**: EU AI Act Article 14 mapping — human oversight measures (linked to WEB-07)
- [ ] **REG-05**: EU AI Act Article 17 mapping — quality management system (audit trail + session history)
- [ ] **REG-06**: Regulatory mapping section explicitly cross-references report content to regulation articles
- [ ] **REG-07**: Disclaimer stating report is guidance, not legal certification; recommend legal counsel review

### Mitigation

- [ ] **MIT-01**: Pre-processing mitigation: Reweighing algorithm
- [ ] **MIT-02**: Pre-processing mitigation: Disparate Impact Remover
- [ ] **MIT-03**: In-processing mitigation: Adversarial Debiasing
- [ ] **MIT-04**: Post-processing mitigation: Equalized Odds Post-processing
- [ ] **MIT-05**: Post-processing mitigation: Calibrated Equalized Odds
- [ ] **MIT-06**: Post-processing mitigation: Reject Option Classification
- [ ] **MIT-07**: Before/after metric comparison displayed after mitigation applied
- [ ] **MIT-08**: Mitigation enforces train/test split — mitigation applied only to training data

### Integration

- [ ] **INT-01**: TUI → Web handoff: [W] hotkey spawns Vite server with session_id in URL
- [ ] **INT-02**: Port discovery: FastAPI writes port to ~/.faircheck/port; TUI/Web read it
- [ ] **INT-03**: Health check polling: TUI polls GET /api/health before opening browser
- [ ] **INT-04**: PID file management: ~/.faircheck/server.pid prevents duplicate FastAPI instances
- [ ] **INT-05**: End-to-end flow: model upload → bias analysis → mitigation → report download works across both interfaces

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### TUI Enhancements

- **TUI-08**: Model diff — compare two model versions side-by-side for bias regression detection
- **TUI-09**: Mitigation wizard — interactive step-through to apply and preview mitigation
- **TUI-10**: Watch mode — `--watch` flag re-runs scan on file change
- **TUI-11**: Config file — `.faircheckrc` per-project thresholds and protected attribute mappings

### Web Enhancements

- **WEB-08**: Mitigation comparison view — before/after charts showing metric change
- **WEB-09**: Model registry — portfolio view of all models, risk levels, last audit dates
- **WEB-10**: Annotation layer — compliance officer can add notes to any metric
- **WEB-11**: Role-based views — toggle Developer vs Compliance view
- **WEB-12**: XLSX export for raw metric data

### Advanced Analysis

- **ADV-01**: Intersectional bias analysis (multi-attribute subgroups)
- **ADV-02**: Model explainability integration (SHAP/LIME alongside fairness metrics)
- **ADV-03**: Post-deployment continuous monitoring integration

### India DPDPA

- **DPDPA-01**: India DPDPA report template
- **DPDPA-02**: Hindi metadata localization
- **DPDPA-03**: Indian HR tech vendor integration patterns

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cloud/SaaS hosting | Local-first is core value prop; deferred to post-v1 SaaS pivot |
| Multi-user collaboration | Single-user tool; enterprise SSO/permissions add months |
| Real-time production monitoring | MLOps territory (Evidently AI, WhyLabs); not an audit tool feature |
| Model training or fine-tuning | Audit tool, not training platform |
| Custom metric definition UI | Over-engineering; config file sufficient for v1 |
| Auto-remediation (unattended bias fix) | Dangerous without human judgment; legal and ethical liability |
| Mobile app | Desktop/terminal-only tool |
| OAuth/SSO | Not needed for local-first single-user tool |
| Video walkthroughs | P2 nice-to-have; not v1 |
| Slack/webhook notifications | P2 nice-to-have; not v1 |
| HuggingFace model ingestion | P1 enhancement; sklearn/joblib/ONNX sufficient for v1 |
| Next.js migration | Deferred until SaaS pivot requires SSR/auth |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENG-01 | Phase 1 | Pending |
| ENG-02 | Phase 1 | Pending |
| ENG-03 | Phase 1 | Pending |
| ING-01 | Phase 2 | Pending |
| ING-02 | Phase 2 | Pending |
| ING-03 | Phase 2 | Pending |
| ING-04 | Phase 2 | Pending |
| ING-05 | Phase 2 | Pending |
| ING-06 | Phase 2 | Pending |
| ING-07 | Phase 2 | Pending |
| ING-08 | Phase 2 | Pending |
| ING-09 | Phase 2 | Pending |
| BIAS-01 | Phase 3 | Pending |
| BIAS-02 | Phase 3 | Pending |
| BIAS-03 | Phase 3 | Pending |
| BIAS-04 | Phase 3 | Pending |
| BIAS-05 | Phase 3 | Pending |
| BIAS-06 | Phase 3 | Pending |
| BIAS-07 | Phase 3 | Pending |
| BIAS-08 | Phase 3 | Pending |
| BIAS-09 | Phase 3 | Pending |
| API-01 | Phase 4 | Pending |
| API-02 | Phase 4 | Pending |
| API-03 | Phase 4 | Pending |
| API-04 | Phase 4 | Pending |
| API-05 | Phase 4 | Pending |
| API-06 | Phase 4 | Pending |
| API-07 | Phase 4 | Pending |
| API-08 | Phase 4 | Pending |
| SESS-01 | Phase 5 | Pending |
| SESS-02 | Phase 5 | Pending |
| SESS-03 | Phase 5 | Pending |
| SESS-04 | Phase 5 | Pending |
| SESS-05 | Phase 5 | Pending |
| TUI-01 | Phase 6 | Pending |
| TUI-02 | Phase 6 | Pending |
| TUI-03 | Phase 6 | Pending |
| TUI-04 | Phase 6 | Pending |
| TUI-05 | Phase 6 | Pending |
| TUI-06 | Phase 6 | Pending |
| TUI-07 | Phase 6 | Pending |
| RPT-01 | Phase 7 | Pending |
| RPT-02 | Phase 7 | Pending |
| RPT-03 | Phase 7 | Pending |
| RPT-04 | Phase 7 | Pending |
| RPT-05 | Phase 7 | Pending |
| RPT-06 | Phase 7 | Pending |
| RPT-07 | Phase 7 | Pending |
| RPT-08 | Phase 7 | Pending |
| RPT-09 | Phase 7 | Pending |
| RPT-10 | Phase 7 | Pending |
| RPT-11 | Phase 7 | Pending |
| WEB-01 | Phase 8 | Pending |
| WEB-02 | Phase 8 | Pending |
| WEB-03 | Phase 8 | Pending |
| WEB-04 | Phase 8 | Pending |
| WEB-05 | Phase 8 | Pending |
| WEB-06 | Phase 8 | Pending |
| WEB-07 | Phase 8 | Pending |
| MIT-01 | Phase 9 | Pending |
| MIT-02 | Phase 9 | Pending |
| MIT-03 | Phase 9 | Pending |
| MIT-04 | Phase 9 | Pending |
| MIT-05 | Phase 9 | Pending |
| MIT-06 | Phase 9 | Pending |
| MIT-07 | Phase 9 | Pending |
| MIT-08 | Phase 9 | Pending |
| REG-01 | Phase 10 | Pending |
| REG-02 | Phase 10 | Pending |
| REG-03 | Phase 10 | Pending |
| REG-04 | Phase 10 | Pending |
| REG-05 | Phase 10 | Pending |
| REG-06 | Phase 10 | Pending |
| REG-07 | Phase 10 | Pending |
| INT-01 | Phase 11 | Pending |
| INT-02 | Phase 11 | Pending |
| INT-03 | Phase 11 | Pending |
| INT-04 | Phase 11 | Pending |
| INT-05 | Phase 11 | Pending |

**Coverage:**
- v1 requirements: 72 total
- Mapped to phases: 72
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-10*
*Last updated: 2026-04-10 after initial definition*

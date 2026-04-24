<p align="center">
  <h1 align="center">⚖️ FairCheck</h1>
  <p align="center">
    <strong>AI Bias Detection & Fairness Auditing Platform</strong>
  </p>
  <p align="center">
    From model upload to regulation-ready PDF — in under 20 minutes.
  </p>
  <p align="center">
    <a href="#-features">Features</a> · <a href="#-quick-start">Quick Start</a> · <a href="#%EF%B8%8F-architecture">Architecture</a> · <a href="#-api-reference">API Reference</a> · <a href="#-sample-datasets">Samples</a> · <a href="#-license">License</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+" />
    <img src="https://img.shields.io/badge/react-19-61DAFB?logo=react&logoColor=black" alt="React 19" />
    <img src="https://img.shields.io/badge/fastapi-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
    <img src="https://img.shields.io/badge/local--first-no%20cloud-orange" alt="Local-first" />
  </p>
</p>

---

## 📖 Overview

FairCheck is an **end-to-end, local-first** AI bias detection and fairness auditing platform. It bridges the gap between data science tooling and compliance-ready governance — delivering a complete pipeline from raw model ingestion to downloadable audit reports.

**Built for two audiences:**

| Interface | Audience | Description |
|-----------|----------|-------------|
| 🖥️ **Web Dashboard** | Compliance teams | Interactive visualizations, drag-and-drop uploads, one-click PDF reports |
| ⚡ **FastAPI Engine** | Developers & integrators | REST API with Swagger docs, scriptable automation |
| 💻 **Terminal UI** *(Planned)* | DevOps & SSH users | ink-based React-in-terminal, scriptable via CLI |

> **🔒 Local-first guarantee:** No model data or datasets are ever transmitted to the cloud. The entire engine runs on your machine. Your data stays yours.

---

## ✨ Features

### 🔬 Bias Analysis Engine

- **6 Fairness Metrics** with configurable thresholds:

  | Metric | Type | Default Threshold | Description |
  |--------|------|:-----------------:|-------------|
  | Demographic Parity Difference | Group | 0.10 | Difference in positive outcome rates across groups |
  | Equalized Odds Difference | Group | 0.10 | Difference in TPR/FPR across groups |
  | Disparate Impact Ratio (4/5ths Rule) | Group | 0.80 | Ratio of selection rates — EEOC standard |
  | Predictive Parity | Group | 0.10 | Difference in positive predictive values |
  | Calibration by Group | Group | 0.05 | Calibration consistency across demographics |
  | Individual Fairness | Individual | 0.80 | Similar individuals receive similar outcomes |

### 🛠️ Live Bias Mitigation Pipeline

- **6 Mitigation Algorithms** spanning pre-, in-, and post-processing — **actually executed with real data**, producing verifiable before/after metric comparisons:

  | Algorithm | Stage | Library | Description |
  |-----------|-------|---------|-------------|
  | Reweighing | Pre-processing | Fairlearn / AIF360 | Reweights training samples to equalize selection rates |
  | Disparate Impact Remover | Pre-processing | AIF360 | Transforms features to remove correlation with protected attributes |
  | Equalized Odds | Post-processing | Fairlearn | Adjusts predictions to equalize TPR/FPR per group |
  | Calibrated Equalized Odds | Post-processing | AIF360 | Calibration-preserving equalized odds |
  | Reject Option Classification | Post-processing | AIF360 | Reassigns predictions near the decision boundary |
  | Adversarial Debiasing | In-processing | AIF360 | Trains adversarial network to remove protected attribute signal |

- **Before/After Comparison** — Every mitigation execution produces a full metric re-evaluation showing improved, degraded, and unchanged metrics inline.
- **Scan Data Caching** — Model and dataset artifacts are automatically cached after scan so mitigation can re-load and execute without re-uploading.

### 🤖 Smart Mitigation Guidance

- **Auto-Recommend Engine** — Inspects detected bias patterns and ranks mitigation algorithms by likely effectiveness, with confidence levels (`HIGH` / `MEDIUM` / `LOW`) and plain-English rationale.
- **Context-Aware Prioritization** — Post-processing (least invasive) ranked before pre-processing before in-processing. Algorithms are matched to the specific failing metrics detected in your scan.
- **One-Click Execute** — Apply any recommended algorithm directly from the dashboard with real-time before/after results.

### 🔍 Advanced Analysis

- **Intersectional Bias Detection** — Analyses pairwise attribute combinations (e.g., `gender × race × age`) to uncover compound discrimination that single-attribute analysis misses. Surfaces hidden subgroup bias required by EU AI Act Article 10.
- **Model Comparison / Diff** — Side-by-side comparison of any two audit sessions. Use to track pre- vs post-mitigation changes, compare candidate models, or build audit trails. Shows per-metric deltas with improved/degraded/unchanged indicators.
- **SHAP-Based Feature Attribution** — Permutation importance per demographic group to identify proxy features that drive bias disparities.
- **Bootstrap Confidence Intervals** — Statistical significance testing (500 bootstrap iterations, 95% CI) prevents false flags from small subgroup noise.
- **Temporal Drift Monitoring** — Compare fairness metrics between audit sessions to detect model degradation over time, with threshold-crossing alerts.
- **Per-Group Performance Breakdown** — Accuracy, precision, recall, and F1 computed per demographic subgroup via Fairlearn's MetricFrame.
- **Plain-English Explanations** — Every metric result is translated into compliance-officer-friendly language with actionable next steps.

### 📋 Compliance & Regulation

- **EU AI Act Mapping** — Automated mapping to Articles 9, 10, 13, 14, and 17 with evidence generation:

  | Article | Title | What FairCheck Maps |
  |---------|-------|---------------------|
  | Article 9 | Risk Management System | Bias analysis results + mitigation evidence |
  | Article 10 | Data and Data Governance | Training data description + demographic breakdown |
  | Article 13 | Transparency | Model card, intended use, known limitations |
  | Article 14 | Human Oversight | Oversight decision records and sign-off |
  | Article 17 | Quality Management | Audit session tracking and trail |

- **Risk Classification** — Automatic `high` / `medium` / `low` classification from the metric ensemble.
- **Compliance Status** — Each article mapped as `addressed`, `partially_addressed`, or `not_addressed`.
- **Human Oversight Workflow** — Record reviewer identity, decision, and notes — locked until sign-off for PDF export.

### 🏢 Domain-Aware Guidance

- Built-in recommendations for **Hiring**, **Lending**, and **Healthcare** with domain-specific thresholds and applicable regulations:

  | Domain | Key Metrics | Regulations |
  |--------|-------------|-------------|
  | **Hiring** | Demographic Parity, Disparate Impact (4/5ths rule) | EEOC Guidelines, EU AI Act Art. 10 |
  | **Lending** | Equalized Odds, Predictive Parity | ECOA, EU AI Act Art. 9 |
  | **Healthcare** | Calibration by Group, Equalized Odds | EU AI Act Art. 9, FDA AI/ML Guidelines |

### 📄 Report Generation

- **PDF Reports** — Via Jinja2 templates + WeasyPrint, regulation-ready format with executive summary, risk heatmap, and sign-off section.
- **Accessible HTML Reports** — WCAG AA compliant standalone HTML with skip-nav links, ARIA labels, semantic headings, high-contrast colors, and screen-reader-friendly data tables. Includes:
  - Executive summary with pass/warn/fail statistics
  - Risk heatmap across all attributes and metrics
  - Remediation timeline showing mitigation history
  - Recommendation table ranked by confidence
  - Compliance sign-off section with signature lines
- **DOCX Reports** — Via python-docx for editable Word documents.
- **Client-Side PDF Export** — One-click download from the web dashboard via `jsPDF` and `html2canvas`, capturing the exact bento-grid layout in high fidelity.
- **Metric Visualizations** — Matplotlib charts embedded in server-generated reports.
- **4 Output Formats** — PDF, HTML, Markdown, DOCX — all from one API endpoint.

### 🖥️ Web Dashboard

- **Modern UI** — React 19 + Vite + Tailwind CSS 4 with a professional bento-grid layout.
- **Interactive Charts** — Recharts-powered visualizations for all fairness metrics.
- **Drag-and-Drop Upload** — Upload `.pkl`, `.joblib`, or `.onnx` models alongside CSV/Parquet/JSON datasets.
- **Toast Notifications** — Real-time feedback for all actions (mitigation applied, oversight recorded, report exported).
- **Auto-Refresh Sidebar** — Persistent session history with full management (start new audits, delete past sessions).
- **Bento Dashboard Panels:**
  - 📊 Bias metric charts with pass/warning/fail indicators
  - 🎯 Risk score card with overall risk level
  - 🔄 Mitigation panel with **live execution** and before/after results
  - 🔀 **Model comparison** panel — side-by-side session diff with delta values
  - 📈 Drift monitoring with session comparison
  - 🔬 Feature attribution visualization
  - 🧬 Intersectional analysis heatmaps
  - 📏 Confidence intervals display
  - 📝 Plain-English explanations panel
  - 👤 Human oversight sign-off form
  - 📑 Regulation selector and compliance status
  - 📥 One-click PDF/DOCX/HTML export

### 📦 Model & Dataset Support

- **Model Formats:** `.pkl` (scikit-learn), `.joblib`, `.onnx` (ONNX Runtime)
- **Dataset Formats:** CSV, Parquet, JSON
- **Auto-Detection:** Protected attributes auto-detected from column names or configurable via `.faircheckrc`

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Engine backend |
| **Node.js** | 20+ | Web dashboard |
| **uv** | latest | Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/)) |

### 1. Clone the Repository

```bash
git clone https://github.com/JUSTMEETPATEL/Google-Solutions.git
cd Google-Solutions
```

### 2. Set Up the Python Engine

```bash
# Install uv (if not already installed)
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
uv sync
```

#### Activate the Virtual Environment

```bash
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# macOS / Linux:
source .venv/bin/activate
```

### 3. Set Up the Web Dashboard

```bash
cd web
npm install
cd ..
```

### 4. Run the Application

You need **two terminals**, both starting from the project root:

#### Terminal 1 — Start the Engine

```bash
# Windows:
.venv\Scripts\python.exe -m faircheck.api.server

# macOS / Linux:
.venv/bin/python -m faircheck.api.server
```

The server auto-selects a free port and prints it:

```
  [FairCheck] API starting on http://127.0.0.1:<port>
```

> The server writes a port file to `~/.faircheck/` for automatic discovery by the web dashboard.

#### Terminal 2 — Start the Web Dashboard

```bash
cd web
npm run dev
```

The Vite dev server starts at:

```
http://localhost:5173
```

### 5. Open in Browser

| URL | Description |
|-----|-------------|
| `http://localhost:5173` | Web Dashboard |
| `http://127.0.0.1:<port>/docs` | Interactive Swagger UI (API Docs) |
| `http://127.0.0.1:<port>/redoc` | ReDoc API Documentation |

### 6. Run Your First Scan

1. Open the Web Dashboard at `http://localhost:5173`
2. Drag & drop a model file (`.pkl` / `.joblib` / `.onnx`)
3. Drag & drop a dataset file (`.csv` / `.parquet` / `.json`)
4. Select protected attributes (e.g., `gender`, `race`)
5. Click **Scan** — results appear in under 60 seconds
6. Review metrics, apply mitigation if needed, export PDF

> **💡 Tip:** Sample models and datasets are included in the `samples/` directory to get started immediately.

---

## 📁 Sample Datasets

Pre-built models and datasets are included for testing across different domains:

| Domain | Model | Dataset | Use Case |
|--------|-------|---------|----------|
| **Hiring** | `hiring_model.pkl` | `hiring_data.csv` | Employee selection bias |
| **Hiring Promotion** | `hiring_promotion_model.pkl` | `hiring_promotion_data.csv` | Promotion decision fairness |
| **Lending** | `lending_credit_model.pkl` | `lending_credit_data.csv` | Credit approval bias |
| **Healthcare** | `healthcare_triage_model.pkl` | `healthcare_triage_data.csv` | Patient triage fairness |
| **Insurance** | `insurance_claims_model.pkl` | `insurance_claims_data.csv` | Claims processing bias |
| **Education** | `education_admission_model.pkl` | `education_admission_data.csv` | Admission decision fairness |
| **Criminal Justice** | `criminal_recidivism_model.pkl` | `criminal_recidivism_data.csv` | Recidivism prediction bias |

```bash
# Quick test via API
cd samples
python test_scan.py
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              FairCheck                                   │
├───────────────┬─────────────────────────┬────────────────────────────────┤
│   Web UI      │     TUI (Planned)       │        FastAPI Engine          │
│   :5173       │     ink (React-TTY)     │        :auto-port              │
│   React 19    │     Commander.js        │        Uvicorn                 │
├───────────────┴─────────────────────────┴────────────────────────────────┤
│                         REST API  (/api/v1)                              │
│  /scan /sessions /sessions/compare /mitigate /reports /oversight /drift   │
├──────────────────────────────────────────────────────────────────────────┤
│                          Analysis Engine                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────────────────┐ │
│  │Ingestion │ │6 Metrics │ │ 6 Mitigation │ │  Advanced Analysis      │ │
│  │.pkl .onnx│ │Group +   │ │  Algorithms  │ │  • Intersectional       │ │
│  │.joblib   │ │Individual│ │  Pre/In/Post │ │  • Feature Attribution  │ │
│  │CSV/JSON  │ │Fairness  │ │  Processing  │ │  • Confidence Intervals │ │
│  │Parquet   │ │          │ │              │ │  • Drift Monitoring     │ │
│  └──────────┘ └──────────┘ └──────────────┘ │  • Explanations         │ │
│                                              │  • Recommendations      │ │
│                                              └─────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│    Report Engine — Jinja2 + WeasyPrint (PDF) + WCAG HTML + python-docx   │
│          EU AI Act Mapping — Articles 9, 10, 13, 14, 17                  │
├──────────────────────────────────────────────────────────────────────────┤
│            SQLite (WAL mode) — ~/.faircheck/sessions.db                  │
│            Alembic — Schema migrations                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Google-Solutions/
├── src/faircheck/              # Python engine (core library)
│   ├── analysis/               # Bias analysis modules
│   │   ├── metrics/            # 6 fairness metric implementations
│   │   │   ├── base.py         # BaseMetric abstract class
│   │   │   ├── demographic_parity.py
│   │   │   ├── equalized_odds.py
│   │   │   ├── disparate_impact.py
│   │   │   ├── predictive_parity.py
│   │   │   ├── calibration.py
│   │   │   └── individual_fairness.py
│   │   ├── engine.py           # Main analysis orchestrator
│   │   ├── intersectional.py   # Pairwise attribute combinations
│   │   ├── feature_attribution.py  # Permutation importance per group
│   │   ├── significance.py     # Bootstrap confidence intervals
│   │   ├── drift.py            # Temporal metric drift detection
│   │   ├── explanations.py     # Plain-English metric explanations
│   │   ├── recommend.py        # Auto-mitigation recommendations
│   │   ├── breakdown.py        # Per-group performance breakdown
│   │   └── domains.py          # Domain-specific guidance
│   ├── mitigation/             # Bias mitigation algorithms
│   │   ├── base.py             # BaseMitigator abstract class
│   │   ├── pipeline.py         # Mitigation orchestrator
│   │   ├── reweighing.py
│   │   ├── equalized_odds.py
│   │   ├── calibrated_eq_odds.py
│   │   ├── disparate_impact_remover.py
│   │   ├── reject_option.py
│   │   └── adversarial_debiasing.py
│   ├── ingestion/              # Model & dataset ingestion
│   │   ├── models.py           # .pkl, .joblib, .onnx loaders
│   │   ├── datasets.py         # CSV, Parquet, JSON loaders
│   │   └── pipeline.py         # Ingestion orchestrator
│   ├── reports/                # Report generation
│   │   ├── engine.py           # Report orchestrator
│   │   ├── renderers.py        # PDF + DOCX + Accessible HTML renderers
│   │   ├── regulation.py       # EU AI Act article mapping
│   │   ├── charts.py           # Matplotlib chart generation
│   │   ├── data.py             # ReportData container
│   │   └── templates/          # Jinja2 templates (PDF, HTML, WCAG)
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # App factory, middleware, router mounts
│   │   ├── server.py           # Uvicorn launcher with port discovery
│   │   ├── lifecycle.py        # PID/port file management
│   │   ├── cache.py            # Scan artifact caching for mitigation
│   │   ├── db.py               # SQLAlchemy session factory
│   │   ├── models.py           # ORM models
│   │   ├── errors.py           # RFC 7807 error handlers
│   │   └── routers/            # API endpoint handlers
│   │       ├── scan.py         # POST /scan — run bias analysis
│   │       ├── sessions.py     # GET/POST /sessions — CRUD + compare
│   │       ├── mitigate.py     # POST /mitigate — execute mitigation
│   │       ├── reports.py      # POST /reports — PDF/HTML/DOCX/MD
│   │       ├── oversight.py    # POST /oversight — human sign-off
│   │       ├── drift.py        # POST /drift — temporal comparison
│   │       └── health.py       # GET /health — health check
│   └── config.py               # TOML config loader with defaults
├── web/                        # React web dashboard
│   ├── src/
│   │   ├── components/         # UI components
│   │   │   ├── Dashboard.tsx         # Main bento-grid layout
│   │   │   ├── FileUpload.tsx        # Drag-and-drop upload
│   │   │   ├── BiasCharts.tsx        # Metric visualizations
│   │   │   ├── RiskScoreCard.tsx     # Overall risk display
│   │   │   ├── MitigationPanel.tsx   # Live execution + before/after
│   │   │   ├── ComparisonPanel.tsx   # Model diff / session comparison
│   │   │   ├── Toast.tsx             # Toast notification system
│   │   │   ├── DriftMonitor.tsx      # Temporal drift tracking
│   │   │   ├── FeatureAttributionPanel.tsx
│   │   │   ├── IntersectionalPanel.tsx
│   │   │   ├── ConfidenceIntervalsPanel.tsx
│   │   │   ├── ExplanationsPanel.tsx
│   │   │   ├── OversightForm.tsx     # Human sign-off
│   │   │   ├── RegulationSelector.tsx
│   │   │   ├── PDFExport.tsx         # Client-side PDF
│   │   │   └── Sidebar.tsx           # Auto-refreshing navigation
│   │   ├── api/client.ts       # API client (TanStack Query)
│   │   ├── store/appStore.ts   # Zustand state management
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── samples/                    # Pre-built models & datasets (7 domains)
├── tests/                      # Pytest test suite
├── alembic/                    # Database migrations
├── tui/                        # Terminal UI (planned)
├── .faircheckrc                # Default configuration (TOML)
└── pyproject.toml              # Python project metadata
```

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`. Full interactive documentation is available at `/docs` when the engine is running.

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — returns `{ "status": "ok" }` |
| `POST` | `/scan` | Upload model + dataset, run full bias analysis |
| `GET` | `/sessions` | List all past scan sessions |
| `GET` | `/sessions/{id}` | Get details of a specific session |
| `DELETE` | `/sessions/{id}` | Delete a scan session |
| `POST` | `/sessions/compare` | Side-by-side comparison of two sessions |
| `POST` | `/mitigate` | **Execute** a mitigation algorithm with before/after results |
| `POST` | `/mitigate/recommend` | Get auto-recommended algorithms for a session |
| `POST` | `/reports` | Generate audit report (PDF, HTML, DOCX, or Markdown) |
| `POST` | `/oversight` | Record a human oversight decision |

### Drift Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/drift/compare` | Compare two sessions for metric drift |
| `GET` | `/drift/history/{model_name}` | Get audit history for a model |

### Example: Run a Scan

```bash
curl -X POST http://127.0.0.1:<port>/api/v1/scan \
  -F "model=@samples/hiring_model.pkl" \
  -F "dataset=@samples/hiring_data.csv" \
  -F "target_column=hired" \
  -F "protected_attributes=gender,race"
```

### Example: Execute Mitigation

```bash
curl -X POST http://127.0.0.1:<port>/api/v1/mitigate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session-id>", "algorithm": "equalized_odds"}'
```

### Example: Compare Two Models

```bash
curl -X POST http://127.0.0.1:<port>/api/v1/sessions/compare \
  -H "Content-Type: application/json" \
  -d '{"session_a": "<baseline-id>", "session_b": "<current-id>"}'
```

### Example: Generate an Accessible HTML Report

```bash
curl -X POST http://127.0.0.1:<port>/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session-id>", "format": "html"}'
```

### Example: Generate a PDF Report

```bash
curl -X POST http://127.0.0.1:<port>/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session-id>", "format": "pdf"}' \
  --output report.pdf
```

---

## ⚙️ Configuration

FairCheck reads from a `.faircheckrc` file (TOML format) in the project root. User-provided values are deep-merged with defaults — you only need to specify what you want to override.

```toml
[metrics]
default_thresholds = {
  demographic_parity_difference = 0.10,
  equalized_odds_difference = 0.10,
  disparate_impact_ratio = 0.80,
  predictive_parity = 0.10,
  calibration_by_group = 0.05,
  individual_fairness = 0.80
}
warning_factor = 0.8   # Metrics at 80%+ of threshold trigger warnings

[individual_fairness]
lipschitz_constant = 1.0
sample_size = 1000

[attributes]
protected = ["gender", "race", "age"]

[report]
format = "pdf"   # "pdf" or "docx"
```

If no `.faircheckrc` is found, FairCheck uses sensible defaults for all values.

---

## 🧪 Running Tests

```bash
# Activate the virtual environment first, then:

# Run all tests
uv run pytest tests/ -v

# Run specific test suites
uv run pytest tests/analysis/ -v        # Analysis engine tests
uv run pytest tests/api/ -v             # API endpoint tests
uv run pytest tests/mitigation/ -v      # Mitigation algorithm tests
uv run pytest tests/reports/ -v         # Report generation tests
uv run pytest tests/test_ingestion.py -v  # Ingestion pipeline tests

# Run with coverage
uv run pytest tests/ -v --cov=faircheck
```

---

## 🛠️ Technology Stack

### Engine Layer (Python)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.11+ | Core runtime |
| Bias Analysis | Fairlearn (primary) + AIF360 (extended) | 0.13+ / 0.6+ | 6 metrics + 6 mitigation algorithms |
| Web Framework | FastAPI | 0.115+ | Async REST API with auto-docs |
| Database | SQLite via SQLAlchemy | 2.0+ | Local-first session persistence (WAL mode) |
| Model Ingestion | scikit-learn + joblib + ONNX Runtime | latest | `.pkl`, `.joblib`, `.onnx` support |
| Data I/O | pandas + pyarrow | 3.0+ / 15+ | CSV, Parquet, JSON |
| Report Templates | Jinja2 | 3.1+ | HTML template engine |
| PDF Generation | WeasyPrint | 62+ | HTML/CSS → PDF |
| DOCX Generation | python-docx | 1.1+ | Programmatic Word documents |
| Charts | Matplotlib | 3.8+ | Metric visualizations for reports |
| Migrations | Alembic | 1.13+ | Database schema versioning |
| Validation | Pydantic | 2.7+ | Type-safe request/response models |

### Web Layer (TypeScript)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Bundler | Vite | 5+ | Fast HMR, ESM-native |
| Framework | React + TypeScript | 19 / 6.0+ | Component-based UI |
| Styling | Tailwind CSS | 4+ | Utility-first CSS |
| Charts | Recharts | 3+ | Interactive data visualizations |
| State | Zustand | 5+ | Lightweight global state |
| Data Fetching | TanStack Query | 5+ | Caching & background refresh |
| File Upload | react-dropzone | 15+ | Drag-and-drop interface |
| PDF Export | jsPDF + html2canvas | latest | High-fidelity client-side PDF generation |
| Icons | Lucide React | latest | Consistent iconography |

### TUI Layer *(Planned)*

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | ink 5 (React-in-terminal) | SSH-compatible terminal UI |
| CLI Parser | Commander.js | Command parsing & help generation |

---

## 🗺️ Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **M0** | Project scaffold, FastAPI skeleton, SQLite setup | ✅ Done |
| **M1** | Model & dataset ingestion pipeline | ✅ Done |
| **M2** | Bias analysis engine (6 metrics) | ✅ Done |
| **M3** | Mitigation pipeline (6 algorithms) | ✅ Done |
| **M4** | Report generation (PDF/DOCX, EU AI Act mapping) | ✅ Done |
| **M5** | Web dashboard, advanced analysis, drift monitoring | ✅ Done |
| **M5.5** | Live mitigation execution, model comparison, WCAG HTML reports, smart guidance, persistent session management, image-based PDF reports | ✅ Done |
| **M6** | TUI interface, Docker support, CI/CD integration | 🔲 Planned |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Set up the development environment (see [Quick Start](#-quick-start))
4. Install dev dependencies: `uv sync --group dev`
5. Run tests before committing: `uv run pytest tests/ -v`
6. Commit your changes: `git commit -m 'feat: add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📝 License

The core FairCheck Engine is released under the **MIT License**.

> The advanced compliance web layer will be available on a paid tier in a future release.

---

<p align="center">
  <strong>Built with ❤️ for responsible AI</strong>
  <br />
  <sub>FairCheck — Because fairness shouldn't be an afterthought.</sub>
</p>

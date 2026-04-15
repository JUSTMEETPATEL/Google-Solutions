<p align="center">
  <h1 align="center">FairCheck</h1>
  <p align="center">
    <strong>AI Bias Detection & Fairness Auditing Platform</strong>
  </p>
  <p align="center">
    From model upload to regulation-ready PDF — in under 20 minutes.
  </p>
  <p align="center">
    <a href="#getting-started">Getting Started</a> · <a href="#architecture">Architecture</a> · <a href="#api-reference">API Reference</a> · <a href="#license">License</a>
  </p>
</p>

---

## Overview

FairCheck is an end-to-end, **local-first** AI bias detection and fairness platform. It bridges the gap between data science tooling and compliance-ready governance by delivering a complete pipeline — from raw model ingestion to downloadable audit reports — through three interfaces sharing one engine:

| Interface | Audience | Status |
|-----------|----------|--------|
| **FastAPI Engine** | Core bias analysis, REST API | Active |
| **Web Dashboard** | Compliance teams, visual analysis | Active |
| **Terminal UI (TUI)** | Developers, SSH-compatible, scriptable | Planned |

> **Local-first guarantee:** No model data or datasets are ever transmitted to the cloud. The engine runs entirely on-device.

---

## Key Features

- **6 Fairness Metrics** — Demographic Parity, Equalized Odds, Disparate Impact, Predictive Parity, Calibration by Group, and Individual Fairness
- **6 Mitigation Algorithms** — Reweighing, Disparate Impact Remover, Equalized Odds, Calibrated Equalized Odds, Reject Option Classification, and Adversarial Debiasing
- **EU AI Act Compliance Mapping** — Automated mapping to Articles 9, 10, 13, 14, and 17 with evidence generation
- **Domain-Aware Guidance** — Built-in recommendations for Hiring, Lending, and Healthcare use cases
- **Multi-Format Reports** — PDF (via WeasyPrint) and DOCX (via python-docx) with Jinja2 templates
- **Broad Model Support** — Ingest `.pkl`, `.joblib`, and `.onnx` models via scikit-learn and ONNX Runtime
- **Dataset Flexibility** — CSV, Parquet, and JSON via pandas + pyarrow
- **Modern Web Dashboard** — React 19 + Vite + Tailwind CSS with interactive Recharts visualizations
- **Session Persistence** — SQLite with WAL mode for safe concurrent access between TUI and Web

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FairCheck                               │
├──────────┬──────────────────────────┬───────────────────────────┤
│  Web UI  │      TUI (Planned)       │      FastAPI Engine       │
│  :5173   │      ink (React-TTY)     │      :random_port         │
├──────────┴──────────────────────────┴───────────────────────────┤
│                        REST API (/api/v1)                       │
├─────────────────────────────────────────────────────────────────┤
│  Ingestion  │  Analysis Engine  │  Mitigation  │  Reports       │
│  .pkl .onnx │  6 Metrics        │  6 Algorithms│  PDF / DOCX    │
├─────────────┴───────────────────┴──────────────┴────────────────┤
│            SQLite (WAL) — ~/.faircheck/sessions.db              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

| Tool | Version | Required For |
|------|---------|--------------|
| **Python** | 3.11+ | Engine (backend) |
| **Node.js** | 20+ | Web dashboard |
| **uv** | latest | Python dependency management |

### 1. Clone the Repository

```bash
git clone https://github.com/JUSTMEETPATEL/Google-Solutions.git
cd Google-Solutions
```

### 2. Set Up the Python Engine

```bash
# Create and activate a virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Install uv (if not already installed)
pip install uv

# Sync all Python dependencies
uv sync
```

### 3. Set Up the Web Dashboard

```bash
cd web
npm install
```

### 4. Run the Application

Open **two terminals** (both from the project root):

**Terminal 1 — Start the Engine:**

```bash
# Windows
.venv\Scripts\python.exe -m faircheck.api.server

# macOS / Linux
.venv/bin/python -m faircheck.api.server
```

The server auto-selects a free port and prints it:

```
[FairCheck] API starting on http://127.0.0.1:<port>
```

**Terminal 2 — Start the Web Dashboard:**

```bash
cd web
npm run dev
```

The Vite dev server starts at:

```
http://localhost:5173
```

### 5. Explore

| URL | Description |
|-----|-------------|
| `http://localhost:5173` | Web Dashboard |
| `http://127.0.0.1:<port>/docs` | Interactive API Documentation (Swagger UI) |
| `http://127.0.0.1:<port>/redoc` | Alternative API Documentation (ReDoc) |

---

## API Reference

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/scan` | Upload model + dataset, run bias analysis |
| `GET` | `/sessions` | List past scan sessions |
| `GET` | `/sessions/{id}` | Get details of a specific session |
| `POST` | `/mitigate` | Apply bias mitigation to a scan |
| `POST` | `/reports` | Generate PDF/DOCX audit report |
| `POST` | `/oversight` | Record human oversight decision |

Full interactive docs available at `/docs` when the engine is running.

---

## Configuration

FairCheck reads from a `.faircheckrc` file (TOML format) in the project root:

```toml
[metrics]
default_thresholds = { demographic_parity_difference = 0.10, equalized_odds_difference = 0.10, disparate_impact_ratio = 0.80 }

[attributes]
protected = ["gender", "race", "age"]

[report]
format = "pdf"
```

If no `.faircheckrc` is found, FairCheck uses sensible defaults including additional thresholds for predictive parity (`0.10`), calibration by group (`0.05`), and individual fairness (`0.80`).

---

## Fairness Metrics

| Metric | Type | Default Threshold | Description |
|--------|------|-------------------|-------------|
| Demographic Parity Difference | Group | 0.10 | Difference in selection rates across groups |
| Equalized Odds Difference | Group | 0.10 | Difference in TPR/FPR across groups |
| Disparate Impact Ratio | Group | 0.80 | Ratio of selection rates (4/5ths rule) |
| Predictive Parity | Group | 0.10 | Difference in positive predictive values |
| Calibration by Group | Group | 0.05 | Calibration consistency across demographics |
| Individual Fairness | Global | 0.80 | Similar individuals receive similar outcomes |

---

## Mitigation Algorithms

| Algorithm | Stage | Library | Description |
|-----------|-------|---------|-------------|
| Reweighing | Pre-processing | Fairlearn/AIF360 | Reweights training samples to reduce bias |
| Disparate Impact Remover | Pre-processing | AIF360 | Transforms features to remove correlation with protected attributes |
| Equalized Odds | Post-processing | Fairlearn | Adjusts predictions to equalize TPR/FPR |
| Calibrated Equalized Odds | Post-processing | AIF360 | Calibration-preserving equalized odds |
| Reject Option Classification | Post-processing | AIF360 | Changes predictions near decision boundary |
| Adversarial Debiasing | In-processing | AIF360 | Trains adversarial network to reduce bias |

---

## Regulation Compliance

FairCheck maps analysis results to **EU AI Act** articles with automated evidence generation:

| Article | Title | What FairCheck Maps |
|---------|-------|---------------------|
| Article 9 | Risk Management System | Bias analysis + mitigation evidence |
| Article 10 | Data and Data Governance | Training data description + demographic breakdown |
| Article 13 | Transparency | Model card, intended use, known limitations |
| Article 14 | Human Oversight | Oversight decision records |
| Article 17 | Quality Management | Audit session tracking |

Each mapping includes a compliance status (`addressed`, `partially_addressed`, or `not_addressed`) and supporting evidence text.

---

## Domain Guidance

FairCheck provides domain-specific recommendations with critical thresholds and applicable regulations:

| Domain | Key Metrics | Regulations |
|--------|-------------|-------------|
| **Hiring** | Demographic Parity, Disparate Impact (4/5ths rule) | EEOC Guidelines, EU AI Act Art. 10 |
| **Lending** | Equalized Odds, Predictive Parity | ECOA, EU AI Act Art. 9 |
| **Healthcare** | Calibration by Group, Equalized Odds | EU AI Act Art. 9, FDA AI/ML Guidelines |

---

## Technology Stack

### Engine Layer (Python)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core runtime |
| Bias Analysis | Fairlearn 0.13+ (primary), AIF360 0.6+ (extended) | Fairness metrics & mitigation |
| Web Framework | FastAPI 0.115+ | Async REST API with auto-docs |
| Database | SQLite via SQLAlchemy 2.0+ | Local-first session persistence |
| Model Ingestion | scikit-learn + joblib + ONNX Runtime | .pkl, .joblib, .onnx support |
| Data I/O | pandas 3.0+ + pyarrow | CSV, Parquet, JSON |
| Reports | Jinja2 + WeasyPrint + python-docx | PDF & DOCX generation |
| Charts | Matplotlib | Metric visualizations for reports |
| Migrations | Alembic | Database schema versioning |

### Web Layer (TypeScript)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Bundler | Vite 5+ | Fast HMR, ESM-native |
| Framework | React 19 + TypeScript | Component-based UI |
| Styling | Tailwind CSS 4+ | Utility-first CSS |
| Charts | Recharts 3+ | Interactive data visualizations |
| State | Zustand 5+ | Lightweight state management |
| Data Fetching | TanStack Query 5+ | Caching & background refresh |
| File Upload | react-dropzone | Drag-and-drop model/dataset upload |
| Icons | Lucide React | Consistent iconography |

### TUI Layer (Planned)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | ink 5 (React-in-terminal) | SSH-compatible terminal UI |
| CLI Parser | Commander.js | Command parsing |
| Runtime | Node.js + tsx | TypeScript execution |

---

## Running Tests

```bash
# Activate the virtual environment first, then:
.venv\Scripts\python.exe -m pytest tests/ -v      # Windows
.venv/bin/python -m pytest tests/ -v               # macOS / Linux
```

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| M0 | Project scaffold, FastAPI skeleton, SQLite setup | Done |
| M1 | Model & dataset ingestion pipeline | Done |
| M2 | Bias analysis engine (6 metrics) | Done |
| M3 | Mitigation pipeline (6 algorithms) | Done |
| M4 | Report generation (PDF/DOCX, EU AI Act mapping) | Done |
| M5 | Web dashboard, API integration, session persistence | In Progress |
| M6 | TUI interface, full end-to-end integration | Planned |

---

## License

The core FairCheck Engine is released under the **MIT License**.

> The advanced compliance web layer will be available on a paid tier in a future release.

# ⚖️ FairCheck

**An end-to-end AI bias detection and fairness platform** bridging the gap between data science tooling and compliance-ready governance.

FairCheck delivers a complete pipeline—from raw model ingestion to regulation-ready audit reports—through two interfaces sharing one powerful, local-first engine.

## 🌟 Core Value

Produce **regulation-ready AI bias audit reports in under 20 minutes**—from model upload to downloadable PDF—that a compliance officer can sign off on without needing to understand the underlying data science.

## ✨ Key Features

- 🔒 **100% Local-First Privacy**: No model data or datasets are ever transmitted to the cloud. The engine runs entirely on-device.
- 🚀 **Lightning Fast Workflows**: Go from raw model ingestion to a downloadable audit PDF in minutes.
- 💻 **Dual Interfaces**: 
  - **Developer TUI**: A scriptable, SSH-compatible terminal UI for data scientists and developers.
  - **Compliance Web App**: A modern, visual web application designed specifically for compliance and governance teams.
- 🧠 **Broad Model Support**: Seamlessly ingest `.pkl`, `.joblib`, and `.onnx` models via scikit-learn and ONNX Runtime.
- 📊 **Industry Standard Metrics**: Built on the foundations of trusted libraries like **Fairlearn** and **AIBM360**, offering deep insights and visualization capabilities.

## 🛠️ Technology Stack

FairCheck is built with a state-of-the-art stack to guarantee performance, maintainability, and a seamless developer experience.

### ⚙️ Engine Layer (Backend)
- **Language**: Python 3.11+
- **Core Bias Libraries**: Fairlearn (Primary) & AIF360 (Extended)
- **Web Framework**: FastAPI (Async, auto-docs)
- **Database**: SQLite via SQLAlchemy 2.0+ (Zero-config, portable)
- **Report Generation**: Jinja2 + WeasyPrint + python-docx
- **Data Handling**: pandas + pyarrow

### 🖥️ Native TUI (CLI) Layer
- **Environment**: Node.js
- **Framework**: `ink` (React-in-terminal for component reuse)
- **CLI Parser**: commander.js
- **Network**: node-fetch / axios

### 🌐 Web Presentation Layer
- **Bundler**: Vite 6.x
- **Framework**: React 19 + TypeScript
- **Styling**: Tailwind CSS 4.x + shadcn/ui
- **Data Viz**: Recharts (Accessible, interactive charts)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query

## 🚀 Getting Started

*(Documentation for getting started will be available soon as the engine implementation progresses.)*

## 📜 License

The core FairCheck Engine is released under the **MIT License**.
*(Note: The advanced compliance web layer will be available on a paid tier.)*

# Features Research: AI Bias Detection & Fairness Platform

## Feature Categories

### Table Stakes (Must Have — Users Leave Without These)

#### Model Ingestion
- Accept common ML model formats (pkl, joblib, ONNX)
- Accept standard dataset formats (CSV, Parquet, JSON)
- Automatic column type inference (numeric, categorical, binary)
- Protected attribute auto-detection with user confirmation
- **Complexity:** Medium | **Dependencies:** Engine core

#### Bias Analysis
- Demographic Parity Difference measurement
- Equalized Odds Difference measurement
- Disparate Impact Ratio (4/5ths rule)
- Per-group performance breakdown
- Configurable thresholds with defaults
- Pass/fail/warning status per metric
- **Complexity:** High | **Dependencies:** Model ingestion

#### Report Generation
- PDF export of audit results
- Cover page with model metadata
- Executive summary in plain language
- Per-metric results table with threshold comparison
- Demographic breakdown charts
- Regulatory article cross-reference mapping
- **Complexity:** High | **Dependencies:** Bias analysis

#### CLI Interface
- `faircheck scan model.pkl --dataset data.csv` command
- Terminal-rendered metric summary table
- CI mode with exit code 1 on threshold breach
- Session persistence for later retrieval
- **Complexity:** Medium | **Dependencies:** Engine API

#### Web Dashboard
- Model + dataset upload (drag-and-drop)
- Visual bias metrics charts
- Session history sidebar
- Report download button
- **Complexity:** Medium-High | **Dependencies:** Engine API

### Differentiators (Competitive Advantage)

#### Regulation-Mapped Output
- EU AI Act Article 9/10/13/14/17 template mapping
- Pre-structured report templates per regulation
- Automatic risk classification based on metric results
- **Complexity:** High | **Dependencies:** Report generation
- **Note:** THIS IS THE PRIMARY DIFFERENTIATOR — no competitor does this

#### Human Oversight Log
- Reviewer name, date, decision recording
- Sign-off workflow for audit trail
- EU AI Act Article 14 compliance
- **Complexity:** Medium | **Dependencies:** Web dashboard

#### Dual Interface (TUI + Web)
- TUI `[W]` hotkey to launch web with same session context
- Shared session state via SQLite
- Developer can audit via terminal, compliance officer reviews in browser
- **Complexity:** High | **Dependencies:** Both interfaces + shared state

#### Mitigation Pipeline
- Pre-processing: Reweighing, Disparate Impact Remover
- In-processing: Adversarial Debiasing, Prejudice Remover
- Post-processing: Equalized Odds Post-processing, Calibrated Equalized Odds, ROC
- Before/after comparison
- **Complexity:** Very High | **Dependencies:** Bias analysis

#### Risk Score Card
- Overall risk level (High/Medium/Low) derived from metric ensemble
- Per-metric risk contribution
- Regulation-specific risk thresholds
- **Complexity:** Medium | **Dependencies:** Bias analysis + regulation mapping

### Anti-Features (Deliberately NOT Building)

| Anti-Feature | Warning | Why Avoid |
|-------------|---------|-----------|
| Cloud model upload | High security risk; kills local-first value prop | Enterprises will not upload models to cloud |
| Real-time monitoring | Scope creep into MLOps territory | Evidently AI, WhyLabs own this space |
| Model training | Out of scope; this is an audit tool not a training platform | Would compete with entire ML ecosystem |
| Custom metric definition UI | Over-engineering; config file is sufficient | Adds massive complexity for marginal value |
| Multi-user collaboration | Enterprise feature; not v1 | SSO, permissions, sharing add months of work |
| Auto-remediation | Dangerous; fairness decisions need human judgment | Legal and ethical liability |

## Feature Dependencies

```
Model Ingestion → Bias Analysis → Mitigation Pipeline
                                → Report Generation → Regulation Templates
                                → Risk Score Card
Engine API → TUI Interface → [W] hotkey → Web Launch
          → Web Dashboard → Human Oversight Log
Session Persistence ← both interfaces read/write
```

## Competitive Feature Gap Analysis

| Feature | AIF360 | Fairlearn | What-If | FairCheck (Ours) |
|---------|--------|-----------|---------|-----------------|
| Bias metrics | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ (wrapped) |
| Mitigation | ★★★★★ | ★★★★☆ | ☆☆☆☆☆ | ★★★★☆ (wrapped) |
| Report generation | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ |
| Regulation mapping | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ |
| Web UI | ☆☆☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ |
| CLI/CI integration | ★★☆☆☆ | ★★☆☆☆ | ☆☆☆☆☆ | ★★★★★ |
| Human oversight | ☆☆☆☆☆ | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ |

---
*Researched: 2026-04-10*

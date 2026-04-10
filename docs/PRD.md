# Product Requirements Document
## AI Bias Detection & Fairness Platform
**Version:** 1.0 — April 2026  
**Status:** Draft  
**Owner:** Founder / Product Lead

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Market Opportunity](#3-market-opportunity)
4. [Competitive Landscape](#4-competitive-landscape)
5. [Product Vision & Strategy](#5-product-vision--strategy)
6. [Target Users & Personas](#6-target-users--personas)
7. [Architecture Overview](#7-architecture-overview)
8. [Feature Requirements](#8-feature-requirements)
   - 8.1 TUI (Terminal UI)
   - 8.2 Web App (Vite + React)
   - 8.3 Shared Engine
   - 8.4 Report Generation
9. [Regulatory Requirements](#9-regulatory-requirements)
10. [Go-to-Market Phases](#10-go-to-market-phases)
11. [Technical Stack](#11-technical-stack)
12. [Milestones & Timeline](#12-milestones--timeline)
13. [Success Metrics](#13-success-metrics)
14. [Risks & Mitigations](#14-risks--mitigations)
15. [Open Questions](#15-open-questions)

---

## 1. Executive Summary

This document defines the requirements for an end-to-end AI bias detection and fairness platform that bridges the gap between data science tooling and compliance-ready governance. Unlike existing libraries (IBM AIF360, Fairlearn, Google What-If Tool), this product delivers a complete pipeline — from raw model ingestion to regulation-ready audit reports — through two interfaces sharing one engine: a TUI for developers and a Vite + React web app for compliance teams.

The August 2026 EU AI Act enforcement deadline for high-risk systems is the primary go-to-market forcing function.

---

## 2. Problem Statement

### The Core Gap
Despite 90% of enterprises deploying AI systems, only 18% have fully implemented AI governance frameworks. The missing 82% is not a tooling gap in raw algorithms — it's a gap in *usability and compliance translation*.

**What exists today:**
- IBM AIF360: 70+ fairness metrics, 10 mitigation algorithms — Python library only, no UI, no reports
- Microsoft Fairlearn: Visualization dashboard + mitigation — but explicitly leaves fairness determination to developers; no regulation-ready output
- Google What-If Tool: Manual, interactive — does not scale, produces nothing a compliance officer can sign off on

**What is missing:**
- An end-to-end pipeline that goes from model → bias analysis → mitigation → audit-ready report
- A usable interface for non-data-scientist personas (compliance leads, legal, HR)
- Regulation-specific output templates (EU AI Act, India DPDPA)
- A product that is locally runnable (no cloud dependency for sensitive model data)

### The Compliance Trigger
The EU AI Act classifies hiring tools, promotion systems, and performance management as **high-risk AI systems**, requiring mandatory bias mitigation documentation and human oversight mechanisms. Full enforcement begins **August 2026**. Fines reach €35 million or 7% of global annual turnover for serious violations.

India's DPDPA requires periodic bias and fairness audits for AI systems affecting people's opportunities or access to services — and no incumbent is locally positioned there.

---

## 3. Market Opportunity

| Signal | Data |
|--------|------|
| AI Governance Software Market (2030 projection) | $7.38 billion |
| CAGR | ~51% |
| Enterprises using AI | ~90% |
| Enterprises with full governance frameworks | ~18% |
| **Addressable gap** | **~82% of AI-deploying enterprises** |

The August 2026 EU AI Act enforcement date creates a hard, non-negotiable deadline that converts latent demand into urgent procurement decisions — particularly for HR tech, fintech, and healthcare AI vendors.

---

## 4. Competitive Landscape

### Direct Competitors

| Tool | Owner | Interface | Reports | Regulation-Mapped | Limitation |
|------|-------|-----------|---------|-------------------|------------|
| AIF360 | IBM | Python API only | None | No | Data scientists only; 70+ metrics with no guidance on which to use |
| Fairlearn | Microsoft | Python + dashboard | None | No | Explicitly defers fairness determination to the developer |
| What-If Tool | Google | Browser (manual) | None | No | Manual inspection only; does not scale |
| Aequitas | UChicago | Python API | Basic | No | Research-grade, not enterprise-ready |

### Key Differentiators of This Product
1. **End-to-end pipeline** — ingestion → analysis → mitigation → report, in one tool
2. **Dual interface** — TUI for developers (SSH-compatible, scriptable), web app for compliance teams
3. **Regulation-mapped outputs** — templates pre-structured for EU AI Act Article 9/10/13 and India DPDPA
4. **Locally runnable** — no cloud dependency; sensitive model data never leaves the machine
5. **Open-core strategy** — OSS engine builds developer trust (IBM AIF360 playbook) + paid compliance layer

---

## 5. Product Vision & Strategy

### Vision
> Make AI fairness auditable by anyone — from the data scientist writing the model to the compliance officer signing the report.

### Strategy
**Phase 1 — Developer trust (Open Source Core)**  
Release the bias detection + mitigation engine as MIT-licensed OSS. Target ML engineers. Build GitHub traction and early adoption before enforcement deadline pressure peaks.

**Phase 2 — Compliance wedge (Paid Web Layer)**  
Introduce the Vite + React web app with compliance-facing features: report templates, human oversight logs, audit trails, and regulation-mapped risk scores. EU AI Act enforcement timeline (Aug 2026) is the key sales lever.

**Phase 3 — India expansion**  
No incumbent is locally positioned for the DPDPA market. Localize report templates for Indian regulatory language. Partner with Indian HR tech vendors and BFSI firms.

---

## 6. Target Users & Personas

### Persona 1 — Dev / ML Engineer ("Terminal Maya")
- **Who:** Data scientist or ML engineer at an enterprise or AI startup
- **Environment:** Terminal, SSH, CI/CD pipelines, Python notebooks
- **Primary interface:** TUI
- **Goal:** Run bias checks on model outputs, integrate into pre-deployment pipeline, get quick pass/fail signal
- **Pain:** Existing libraries have no guidance on metric selection; results aren't translatable to stakeholders
- **Key hotkey:** Runs `faircheck scan model.pkl --dataset train.csv` and sees a structured diff-style report

### Persona 2 — Compliance Officer ("Audit Priya")
- **Who:** Legal, compliance, or risk lead at a regulated enterprise
- **Environment:** Browser, no coding, exports to PDF/Word for regulators
- **Primary interface:** Web app (Vite + React, runs locally)
- **Goal:** Produce a signed-off audit document that satisfies the EU AI Act's Article 9 risk management requirements
- **Pain:** Has no visibility into what the data team is doing; receives "we ran the tests" with no documentation
- **Key workflow:** Opens `localhost:5173`, uploads model + dataset, selects "EU AI Act – High Risk", downloads compliance report

### Persona 3 — CTO / Head of AI ("Strategic Sam")
- **Who:** Technical leader accountable for AI governance
- **Environment:** Both; reviews dashboards and signs off on compliance posture
- **Goal:** Portfolio view of all models deployed, risk levels, audit status, mitigation history
- **Pain:** No single pane of glass across models; audit prep is manual and last-minute

---

## 7. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    SHARED ENGINE (Python)                │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │  Ingestion   │  │  Bias Analysis│  │  Mitigation  │ │
│  │  Layer       │→ │  (metrics)    │→ │  Algorithms  │ │
│  │  .pkl/.joblib│  │  demographic  │  │  reweigh,    │ │
│  │  .onnx, API  │  │  parity, etc. │  │  calibration │ │
│  └──────────────┘  └───────────────┘  └──────┬───────┘ │
│                                               │         │
│                                    ┌──────────▼───────┐ │
│                                    │  Report Builder  │ │
│                                    │  (EU AI Act,     │ │
│                                    │   DPDPA, custom) │ │
│                                    └──────────────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │  Engine API (local IPC / REST)
            ┌───────────────┴──────────────┐
            │                              │
  ┌─────────▼──────────┐        ┌──────────▼──────────┐
  │   TUI Interface    │        │  Web App             │
  │   (npm: ink /      │        │  Vite + React        │
  │    blessed /       │        │  localhost:5173       │
  │    terminal-kit)   │        │  [W] hotkey from TUI  │
  │                    │        │  spins up server      │
  └────────────────────┘        └─────────────────────-┘
```

### Key Architectural Decisions
- **Local-first:** Engine runs entirely on-device. No model data transmitted to cloud.
- **TUI → Web handoff:** `[W]` hotkey in TUI starts the Vite dev server and opens the browser to the same session context.
- **Shared session state:** Both interfaces read/write from a local SQLite store (`~/.faircheck/sessions.db`).
- **Engine language:** Python (inherits AIF360/Fairlearn algorithm ecosystem). TUI and Web are Node.js/JavaScript.
- **IPC:** Engine exposes a local REST API on a random port; both UIs communicate over localhost.

---

## 8. Feature Requirements

### 8.1 TUI (Terminal Interface)

**Package options (npm):**
- `ink` — React-in-terminal; best for component-based UIs, hot reload in dev
- `blessed` / `blessed-contrib` — mature, chart support, dashboard layouts
- `terminal-kit` — rich widget library, good for forms and progress bars

**Recommended:** `ink` for component reuse with the web layer; `blessed-contrib` if chart rendering in terminal is a priority.

#### P0 — Must Have (Launch)
| ID | Feature | Description |
|----|---------|-------------|
| TUI-01 | `faircheck scan` | CLI command: accepts model file + dataset CSV. Runs full bias analysis pipeline. |
| TUI-02 | Metric summary view | Terminal-rendered table of key fairness metrics with pass/fail/warning status |
| TUI-03 | Protected attribute detection | Auto-detects likely protected attributes (gender, race, age columns) with confirmation prompt |
| TUI-04 | `[W]` hotkey | Starts Vite web server, opens `localhost:5173` with current session pre-loaded |
| TUI-05 | `[R]` hotkey | Generates PDF/MD report for current session |
| TUI-06 | Session persistence | Saves scan results to `~/.faircheck/sessions.db` |
| TUI-07 | CI mode | `--ci` flag: exits with code 1 if fairness thresholds are breached (for GitHub Actions / pre-commit hooks) |

#### P1 — Should Have (v1.1)
| ID | Feature | Description |
|----|---------|-------------|
| TUI-08 | Model diff | Compare two model versions side-by-side for bias regression detection |
| TUI-09 | Mitigation wizard | Interactive step-through to apply and preview mitigation algorithms |
| TUI-10 | Watch mode | `--watch` flag: re-runs scan on file change (for notebook-style iteration) |
| TUI-11 | Config file | `.faircheckrc` for per-project metric thresholds and protected attribute mappings |

#### P2 — Nice to Have
- TUI-12: Slack/webhook notification on threshold breach
- TUI-13: ANSI color themes (for accessibility)

---

### 8.2 Web App (Vite + React)

**Stack:** Vite 5+ (fastest local dev server, ESM-native), React 18, Tailwind CSS, shadcn/ui components.

**Why Vite over Next.js for this use case:**
- No server-side rendering needed — all data is local
- Faster HMR, simpler config for a local-only tool
- No Node.js server process to manage; Vite dev server is enough
- Next.js adds routing/SSR complexity that is unnecessary for a localhost compliance tool
- If compliance teams later need a hosted SaaS version, Next.js can be adopted at that point

#### P0 — Must Have (Launch)
| ID | Feature | Description |
|----|---------|-------------|
| WEB-01 | Session loader | Reads from local SQLite session; shows scan history in sidebar |
| WEB-02 | Model + dataset uploader | Drag-and-drop upload; files stay local (no network requests) |
| WEB-03 | Bias dashboard | Visual charts: demographic parity, equalized odds, disparate impact ratio by group |
| WEB-04 | Regulation selector | Dropdown: EU AI Act (High Risk), EU AI Act (Limited Risk), India DPDPA, Custom |
| WEB-05 | Risk score card | Overall risk level (High / Medium / Low) with per-metric breakdowns |
| WEB-06 | Report export | One-click PDF export of the compliance report |
| WEB-07 | Human oversight log | Form to record reviewer name, date, decision, and sign-off for the audit trail |

#### P1 — Should Have (v1.1)
| ID | Feature | Description |
|----|---------|-------------|
| WEB-08 | Mitigation comparison view | Before/after charts showing metric change after applying mitigation |
| WEB-09 | Model registry | Portfolio view: all models, their risk level, last audit date, and status |
| WEB-10 | Annotation layer | Compliance officer can add notes to any metric for the report |
| WEB-11 | Role-based views | Toggle between "Developer view" (raw metrics) and "Compliance view" (plain-language summary) |
| WEB-12 | XLSX export | Export raw metric data as spreadsheet for additional analysis |

#### P2 — Nice to Have
- WEB-13: Multi-model comparison dashboard
- WEB-14: Email report delivery
- WEB-15: Embedded video walkthrough for first-time compliance officers

---

### 8.3 Shared Engine

The Python engine is the OSS core and the primary trust-building artifact.

#### Ingestion Layer
- Supported model formats: `.pkl`, `.joblib`, `.onnx`, Hugging Face model ID (local)
- Supported dataset formats: CSV, Parquet, JSON
- Automatic column type inference (numeric, categorical, binary)
- Protected attribute auto-detection with confidence score

#### Bias Analysis
Metric categories (mapped to regulatory requirements):

| Metric | Regulatory Reference | Default Threshold |
|--------|---------------------|-------------------|
| Demographic Parity Difference | EU AI Act Art. 10 | ≤ 0.10 |
| Equalized Odds Difference | EU AI Act Art. 9 | ≤ 0.10 |
| Disparate Impact Ratio | US EEOC 4/5ths rule, DPDPA | ≥ 0.80 |
| Predictive Parity | EU AI Act Art. 13 | ≤ 0.10 |
| Calibration by Group | EU AI Act Art. 9 | ≤ 0.05 |
| Individual Fairness (cosine) | DPDPA | Configurable |

#### Mitigation Algorithms
- Pre-processing: Reweighing, Disparate Impact Remover
- In-processing: Adversarial Debiasing, Prejudice Remover
- Post-processing: Equalized Odds Post-processing, Calibrated Equalized Odds, Reject Option Classification

#### Report Builder
- Template engine: Jinja2
- Output formats: PDF (via WeasyPrint), Markdown, DOCX
- Regulation templates: EU AI Act (Article 9, 10, 13), India DPDPA, generic ISO/IEC 42001 draft

---

### 8.4 Report Generation

Each report must include:

1. **Cover page** — Model name, version, audit date, reviewer, regulation standard
2. **Executive summary** — Plain-language risk verdict (suitable for non-technical stakeholders)
3. **Model card** — Training data description, intended use, known limitations
4. **Bias analysis results** — Per-metric table with threshold, actual value, and status
5. **Demographic breakdown** — Per-group performance charts
6. **Mitigation applied** — Algorithm used, before/after metric comparison
7. **Human oversight record** — Reviewer name, date, decision, signature field
8. **Regulatory mapping** — Explicit cross-reference to regulation articles satisfied
9. **Appendix** — Raw metric data, methodology notes

---

## 9. Regulatory Requirements

### EU AI Act
| Article | Requirement | Product Feature |
|---------|------------|-----------------|
| Art. 9 | Risk management system documentation | Risk score card + report section |
| Art. 10 | Training data governance and bias monitoring | Bias analysis pipeline + demographic breakdown |
| Art. 13 | Transparency and provision of information | Plain-language compliance view + report |
| Art. 14 | Human oversight measures | Human oversight log (WEB-07) |
| Art. 17 | Quality management system | Audit trail + session history |

**Enforcement timeline:**
- February 2025: Prohibited AI practices banned
- August 2025: Governance and literacy obligations active
- **August 2026: High-risk system requirements fully enforceable** ← primary market forcing function
- Fines: up to €35M or 7% of global annual turnover

### India DPDPA
- Periodic bias and fairness audits required for AI affecting opportunities or access to services
- No incumbent locally positioned — first-mover opportunity
- Report templates to be localized in v1.1 (English + Hindi metadata)

---

## 10. Go-to-Market Phases

### Phase 1 — Open Source Core (Months 1–6)
**Goal:** Developer trust and GitHub traction

- Release Python engine as MIT-licensed OSS on GitHub
- TUI as the primary interface
- Target: ML engineers, AI safety researchers, open-source contributors
- Distribution: HackerNews, r/MachineLearning, Papers With Code, Dev.to
- Success: 500 GitHub stars, 50 active contributors, 10 enterprise "watching" signals

### Phase 2 — Compliance Wedge (Months 5–10, before Aug 2026 enforcement)
**Goal:** Convert enterprise urgency into paid web layer adoption

- Launch Vite + React web app as paid add-on or freemium tier
- Primary message: "August 2026 is your deadline. Your report takes 20 minutes."
- Target: EU-based enterprises using AI in HR, hiring, credit, healthcare
- Sales channel: Direct outreach to Chief Compliance Officers, Legal Ops, HR Tech vendors
- Pricing signal: Per-model audit (€99/model/year) or enterprise seat license

### Phase 3 — India Expansion (Months 10–18)
**Goal:** First-mover in DPDPA compliance tooling

- DPDPA report template localisation
- Partner with Indian HR tech players (Darwinbox, Keka, GreytHR) and BFSI firms
- Explore NASSCOM partnership for distribution
- Consider rupee-denominated pricing tier

---

## 11. Technical Stack

### Engine (OSS Core)
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | AIF360/Fairlearn ecosystem compatibility |
| Bias library | AIF360 + Fairlearn (wrapped) | Leverage existing algorithms; avoid reinventing |
| Model ingestion | ONNX Runtime, scikit-learn, joblib | Widest format coverage |
| Report generation | Jinja2 + WeasyPrint | PDF without heavy dependencies |
| Local DB | SQLite (via SQLAlchemy) | Zero-config, file-based, portable |
| API layer | FastAPI (localhost only) | Async, auto-docs, lightweight |

### TUI
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | `ink` (npm) | React component model; code reuse with web layer |
| Charts | `blessed-contrib` (fallback) | Terminal charts for metric visualization |
| Packaging | `pkg` or `nexe` | Single binary distribution, no Node.js install required for end users |

### Web App
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Bundler | Vite 5+ | Fastest local dev server; no SSR overhead needed |
| Framework | React 18 | Component reuse with ink TUI |
| Styling | Tailwind CSS + shadcn/ui | Rapid compliance-grade UI |
| Charts | Recharts | Lightweight, accessible, composable |
| PDF export | react-pdf / jsPDF | Client-side PDF generation; no server round-trip |
| State | Zustand | Simple, no boilerplate |
| Local API client | TanStack Query | Caching + async state for local FastAPI calls |

### Note on Next.js
Next.js is not chosen for v1.0 because the product is local-first and requires no SSR, routing complexity, or server infrastructure. If Phase 2 evolves into a hosted SaaS offering (multi-tenant, cloud-stored audits), migrating the web layer to Next.js App Router is the intended upgrade path.

---

## 12. Milestones & Timeline

| Milestone | Target | Description |
|-----------|--------|-------------|
| M0: Foundations | Month 1 | Repo setup, engine scaffold, AIF360/Fairlearn wrappers, local FastAPI |
| M1: Engine Alpha | Month 2 | Full bias analysis pipeline on CSV + sklearn models; CLI scan command |
| M2: TUI Beta | Month 3 | ink TUI with metric table, session persistence, CI mode, [W] hotkey |
| M3: Web App Alpha | Month 4 | Vite + React dashboard, bias charts, session loader |
| M4: Report v1 | Month 5 | EU AI Act report template, PDF export, human oversight log |
| M5: OSS Launch | Month 6 | GitHub public release, HN post, documentation site |
| M6: Web App Paid | Month 8 | Compliance tier launch, pricing, enterprise onboarding |
| M7: India Templates | Month 12 | DPDPA report template, India GTM |
| **Deadline:** | **Aug 2026** | **EU AI Act high-risk enforcement begins** |

---

## 13. Success Metrics

### Product Metrics
| Metric | 6-Month Target | 12-Month Target |
|--------|---------------|-----------------|
| GitHub stars | 500 | 2,000 |
| Weekly active TUI users | 200 | 1,000 |
| Models audited (total) | 1,000 | 10,000 |
| Reports generated | 500 | 5,000 |
| Enterprise customers (paid) | 5 | 30 |
| ARR | — | €150,000 |

### Compliance Quality Metrics
- Report acceptance rate by regulatory reviewers (target: >90% first-pass acceptance)
- Time-to-report: model upload → downloadable PDF (target: <20 minutes)
- False negative rate on bias detection vs. manual audit (target: <5%)

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| EU AI Act enforcement delayed again | Medium | High | Pivot messaging to DPDPA + ISO 42001; demand exists independently |
| AIF360/Fairlearn API breaking changes | Low | Medium | Pin versions; abstract behind wrapper layer; maintain own fork if needed |
| Enterprise security teams block local tools | Medium | High | Publish security architecture doc; air-gap deployment guide; SOC2 roadmap |
| Competitor (IBM, Microsoft) adds reporting | Medium | High | Speed advantage; OSS moat; regulation-specific templates are defensible |
| India DPDPA enforcement slower than expected | Medium | Low | Phase 3 is opportunistic; Phase 1+2 revenue funds it |
| Fairness metric selection misaligned with regulators | Medium | High | Engage DPA/legal advisors for each jurisdiction; publish methodology openly |

---

## 15. Open Questions

1. **Pricing model:** Per-model-per-year vs. seat license vs. usage-based? Need enterprise discovery calls before Phase 2 launch.
2. **ONNX support scope:** How many model formats to support at launch? Recommend: sklearn, joblib, ONNX as P0; HuggingFace transformers as P1.
3. **Multi-dataset support:** Should a single audit support multiple dataset slices (e.g., train + test + production)? Likely yes for EU AI Act compliance, but increases engine complexity.
4. **Next.js migration trigger:** Define the exact criteria that would prompt migrating the web layer from Vite to Next.js (e.g., "when we need user accounts and cloud storage").
5. **Human oversight log legal weight:** Does a digital log in the tool satisfy EU AI Act Art. 14's human oversight requirement, or does it need wet signature / notarization? Need legal opinion.
6. **India partnership strategy:** Build direct vs. embed in existing HR tech platforms as a white-label module?
7. **OSS governance:** MIT vs. Apache 2.0 vs. AGPL for the engine? AGPL would prevent competitors from forking without contributing back but may deter enterprise adoption.

---

*Document owner: Founder / Product Lead*  
*Next review: Before M2 (TUI Beta) milestone*  
*Changelog: v1.0 — initial draft, April 2026*
# Stack Research: AI Bias Detection & Fairness Platform

## Recommended Stack (2025–2026)

### Engine Layer (Python)

| Component | Recommendation | Version | Confidence | Rationale |
|-----------|---------------|---------|------------|-----------|
| Language | Python | 3.11+ | ★★★★★ | AIF360/Fairlearn ecosystem is Python-native; no viable alternative |
| Bias Library (Primary) | Fairlearn | 0.11+ | ★★★★★ | Active development, Microsoft-backed, cleaner API than AIF360, better `MetricFrame` |
| Bias Library (Extended) | AIF360 | 0.6+ | ★★★★☆ | 70+ metrics, 10 mitigation algorithms; use as supplementary for algorithms Fairlearn lacks |
| Model Ingestion | scikit-learn + joblib + ONNX Runtime | latest | ★★★★★ | Covers .pkl, .joblib, .onnx — widest format coverage |
| Dataset I/O | pandas + pyarrow | pandas 2.2+, pyarrow 15+ | ★★★★★ | CSV, Parquet, JSON natively; pyarrow for Parquet performance |
| Web Framework | FastAPI | 0.115+ | ★★★★★ | Async, auto-docs (Swagger), Pydantic validation, lightweight |
| Database | SQLite via SQLAlchemy | SQLAlchemy 2.0+ | ★★★★★ | Zero-config, file-based, portable; perfect for local-first |
| Report Templates | Jinja2 | 3.1+ | ★★★★★ | Industry standard template engine for Python |
| PDF Generation | WeasyPrint | 62+ | ★★★★☆ | HTML/CSS to PDF; lighter than wkhtmltopdf; no browser dependency |
| DOCX Generation | python-docx | 1.1+ | ★★★★☆ | Programmatic Word document creation |
| Data Validation | Pydantic | 2.7+ | ★★★★★ | Built into FastAPI; type-safe request/response models |
| Task Processing | Starlette BackgroundTasks | built-in | ★★★★☆ | Sufficient for single-user local; no Celery/Redis overhead |

### TUI Layer (Node.js)

| Component | Recommendation | Version | Confidence | Rationale |
|-----------|---------------|---------|------------|-----------|
| Framework | ink | 5.x | ★★★★☆ | React-in-terminal; component reuse with web layer |
| CLI Parser | commander.js | 12+ | ★★★★★ | Mature, well-documented, TypeScript support |
| HTTP Client | node-fetch or axios | latest | ★★★★★ | For FastAPI REST calls |
| Charts | blessed-contrib | latest | ★★★☆☆ | Terminal charts; limited but functional for metric viz |
| Binary Packaging | pkg | 5.x | ★★★☆☆ | Single binary distribution; consider `nexe` as fallback |

### Web Layer (Vite + React)

| Component | Recommendation | Version | Confidence | Rationale |
|-----------|---------------|---------|------------|-----------|
| Bundler | Vite | 6.x | ★★★★★ | Fastest HMR, ESM-native, no SSR overhead |
| Framework | React | 19 | ★★★★★ | Component ecosystem, TUI code reuse via ink |
| Styling | Tailwind CSS | 4.x | ★★★★★ | Utility-first, rapid UI development |
| Components | shadcn/ui | latest | ★★★★★ | Accessible, customizable, Tailwind-native |
| Charts | Recharts | 2.15+ | ★★★★☆ | React-native, composable, WAI-ARIA accessible |
| State | Zustand | 5.x | ★★★★★ | Minimal boilerplate, TypeScript-friendly |
| Data Fetching | TanStack Query | 5.x | ★★★★★ | Caching, background refresh for local API calls |
| PDF Export | react-pdf or jsPDF | latest | ★★★★☆ | Client-side PDF; no server round-trip |
| Type Safety | TypeScript | 5.7+ | ★★★★★ | Non-negotiable for any React project in 2026 |

## What NOT to Use

| Anti-Choice | Why Not |
|-------------|---------|
| Next.js (for v1) | SSR unnecessary for local-first tool; adds complexity without benefit |
| Streamlit | Python-only frontend; no TUI, no component reuse, limited customization |
| Django | Too heavyweight for a local REST API; FastAPI is better fit |
| TensorFlow Fairness Indicators | TF-only; doesn't support sklearn/joblib models |
| Celery/Redis | Over-engineering for single-user local tool; BackgroundTasks sufficient |
| Electron | Too heavy for a CLI-first tool; web via browser is sufficient |
| PostgreSQL | Needs server process; SQLite is zero-config and perfect for local |

## Key Version Considerations

- **Python 3.11+**: Required for AIF360 0.6+; 3.12+ preferred for performance
- **React 19**: Stable since late 2024; use for latest concurrent features
- **Vite 6**: Major ESM improvements; ensure Tailwind v4 compatibility
- **Fairlearn 0.11+**: Introduced improved `ThresholdOptimizer` and better plotting

---
*Researched: 2026-04-10*

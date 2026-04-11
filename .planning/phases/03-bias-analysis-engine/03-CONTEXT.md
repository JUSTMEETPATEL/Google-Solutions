# Phase 03: Bias Analysis Engine - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the 6 core fairness metrics (Demographic Parity, Equalized Odds, Disparate Impact Ratio, Predictive Parity, Calibration by Group, Individual Fairness) with configurable thresholds, per-group performance breakdowns, and domain-specific guidance. This phase builds the core analysis engine that all downstream phases (API, TUI, Web, Reports) depend on.
</domain>

<decisions>
## Implementation Decisions

### Domain Guidance
- **D-01:** **Hardcoded dictionaries:** Domain-specific metric guidance for hiring, lending, and healthcare use cases will be stored as hardcoded Python dictionaries in a `domains.py` module. No external config file I/O needed — simplest approach for v1 with guaranteed availability.

### Edge Case Handling
- **D-02:** **Small sample size — warn and skip:** When a demographic subgroup has too few samples to compute reliable confusion metrics, the engine logs a warning and returns `null` for that subgroup's metrics. The scan continues for all other subgroups — never fails the entire analysis due to a single sparse subgroup.

### Threshold Architecture
- **D-03:** **Threshold evaluation in core math layer:** Each metric class evaluates its own pass/fail/warning status against the configured threshold immediately upon computation. This keeps threshold logic co-located with the math rather than in a separate wrapper.

### Individual Fairness (BIAS-06)
- **D-04:** **Auto-select features with override:** Individual fairness similarity is computed using cosine distance over all non-protected numeric features, auto-normalized. Users can override the similarity feature set via config or API parameter for more domain-specific similarity definitions.

### Warning Zone
- **D-05:** **Configurable warning multiplier:** Warning status is triggered by a configurable multiplier in `.faircheckrc` (default `warning_factor: 0.8`). For a threshold of 0.10, warning fires at 0.08 (i.e., `threshold × warning_factor`). This aligns with the existing Phase 1 configuration system.

### Multi-Attribute Computation
- **D-06:** **Independent per attribute:** When multiple protected attributes are specified (e.g., gender AND race), metrics are computed independently for each attribute. Intersectional analysis (gender × race subgroups) is explicitly deferred to v2 (ADV-01).

### Metric Output Structure
- **D-07:** **Nested JSON by protected attribute:** The engine returns results nested top-level by protected attribute, each containing its metric results. Example structure:
  ```json
  {
    "gender": {
      "demographic_parity": { "value": 0.05, "status": "pass", ... },
      "equalized_odds": { ... }
    },
    "race": {
      "demographic_parity": { ... }
    }
  }
  ```
  This natural grouping simplifies downstream rendering in both TUI tables and web dashboard charts.

### Prior Decisions Kept
- **D-08:** **Strict validation (from Phase 4/D-08):** Invalid or NaN data inputs fail loudly with 400 errors at the API boundary. The engine itself assumes clean data has been validated upstream.
- **D-09:** **JSON column storage (from Phase 5/D-03):** The nested metric output structure aligns with the JSON column storage decision — results are stored as-is in SQLite without flattening.

### Agent's Discretion
- Choice of whether to use Fairlearn's `MetricFrame` directly or wrap individual metric computations.
- Internal class hierarchy for the 6 metric implementations.
- Unit test structure and benchmark dataset selection.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Requirements
- `.planning/PROJECT.md` — Overall architecture constraints and goal (Local-first, Python 3.11, wrapper pattern).
- `.planning/REQUIREMENTS.md` — Phase 3 requirements (BIAS-01 to BIAS-09).

### Prior Phase Context
- `.planning/phases/04-fastapi-server-rest-api/04-CONTEXT.md` — API architecture decisions (modular routing, RFC 7807 errors, synchronous blocking).
- `.planning/phases/05-session-persistence-sqlite/05-CONTEXT.md` — Database decisions (JSON columns, Alembic migrations, synchronous SQLAlchemy).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/faircheck/algorithms/` — Phase 1 wrapper abstractions around AIF360/Fairlearn. The bias analysis engine should use these wrappers exclusively, never importing AIF360/Fairlearn directly.
- `.faircheckrc` config system — Phase 1 configuration loader for metric thresholds and protected attributes.

### Established Patterns
- Wrapper pattern isolating upstream library API changes (ENG-02).
- Configuration system for thresholds and preferences (ENG-03).

### Integration Points
- `src/faircheck/api/routers/scan.py` — Will invoke the bias analysis engine after model/dataset ingestion.
- `src/faircheck/ingestion/pipeline.py` — Provides loaded model + dataset that the engine consumes.
</code_context>

<specifics>
## Specific Ideas

No specific user-provided references or "I want it like X" moments.
</specifics>

<deferred>
## Deferred Ideas

- **Intersectional bias analysis** (gender × race subgroups) — Explicitly deferred to v2 (ADV-01).
- **Dynamic domain guidance from config files** — Hardcoded dictionaries sufficient for v1; config-driven guidance is a v2 enhancement.
</deferred>

---

*Phase: 03-bias-analysis-engine*
*Context gathered: 2026-04-11*

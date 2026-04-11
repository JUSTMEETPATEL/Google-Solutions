# Phase 03: Bias Analysis Engine — Research

**Researched:** 2026-04-11
**Status:** Complete

## RESEARCH COMPLETE

## 1. Library API Mapping — Which Library for Which Metric

### Fairlearn (Primary — `fairlearn.metrics`)

Fairlearn provides **first-class scalar functions** for two of the six metrics:

| Metric | Fairlearn Function | Signature | Notes |
|--------|-------------------|-----------|-------|
| Demographic Parity (BIAS-01) | `demographic_parity_difference()` | `(y_true, y_pred, *, sensitive_features)` → `float` | Standalone scalar; do NOT pass into MetricFrame |
| Equalized Odds (BIAS-02) | `equalized_odds_difference()` | `(y_true, y_pred, *, sensitive_features)` → `float` | Standalone scalar; computes max of TPR diff and FPR diff |

**MetricFrame** is used for per-group breakdowns (BIAS-08), not for top-level metric computation:

```python
from fairlearn.metrics import MetricFrame, true_positive_rate, false_positive_rate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

mf = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "precision": functools.partial(precision_score, zero_division=0),
        "recall": recall_score,
        "f1": functools.partial(f1_score, zero_division=0),
        "tpr": true_positive_rate,
        "fpr": false_positive_rate,
    },
    y_true=y_true,
    y_pred=y_pred,
    sensitive_features=sensitive_features
)
mf.overall       # Series — overall per metric
mf.by_group      # DataFrame — metric × group
mf.difference()  # Series — max disparity per metric
```

**Key constraint:** MetricFrame requires metric functions of signature `fn(y_true, y_pred)`. Extra args must be bound via `functools.partial()`.

### AIF360 (Extended — `aif360.sklearn.metrics`)

Use the **sklearn-compatible API** (`aif360.sklearn.metrics`), NOT the legacy class-based API. Avoids needing `BinaryLabelDataset` conversion.

| Metric | AIF360 Function | Signature | Notes |
|--------|----------------|-----------|-------|
| Disparate Impact Ratio (BIAS-03) | `disparate_impact_ratio()` | `(y_true, y_pred, *, prot_attr, priv_group)` → `float` | Ratio of favorable outcome rates; ideal = 1.0, threshold ≥ 0.80 |
| Predictive Parity (BIAS-04) | Requires manual computation | Use `ClassificationMetric.positive_predictive_value()` per group or compute from confusion matrix | No direct sklearn-style function; compute precision per group and take difference |
| Calibration by Group (BIAS-05) | No direct function | Compute `sklearn.calibration.calibration_curve()` per group, compare | Must implement manually using calibration curves per subgroup |

### Custom Implementation Required

| Metric | Approach | Dependencies |
|--------|----------|-------------|
| Predictive Parity (BIAS-04) | Compute `precision_score` per group via MetricFrame, take max difference | `sklearn.metrics.precision_score`, `fairlearn.metrics.MetricFrame` |
| Calibration by Group (BIAS-05) | Compute calibration error (ECE) per group, take max difference | `sklearn.calibration.calibration_curve` + manual ECE calculation |
| Individual Fairness (BIAS-06) | Cosine distance over non-protected features, Lipschitz consistency check | `sklearn.metrics.pairwise.cosine_similarity`, `sklearn.preprocessing.StandardScaler` |

## 2. Individual Fairness (BIAS-06) — Deep Dive

**Concept (Dwork et al.):** Similar individuals should receive similar treatment. Formally, the Lipschitz condition:

```
|f(x_i) - f(x_j)| ≤ L × d(x_i, x_j)
```

**Implementation approach:**

1. **Feature selection:** Auto-select all numeric non-protected columns. Apply `StandardScaler` normalization.
2. **Pairwise distance:** Use `sklearn.metrics.pairwise.cosine_similarity` → convert to distance (`1 - similarity`).
3. **Output distance:** Compute `|predict_proba(x_i) - predict_proba(x_j)|` for all pairs.
4. **Consistency score:** Fraction of pairs satisfying Lipschitz with configurable `L`. Higher = fairer.

**Scalability concern:** Pairwise computation is O(n²). For large datasets:
- Sample a random subset (e.g., 1000 individuals) for the individual fairness check.
- Document the sampling in the metric result.

**Output structure:**
```json
{
  "individual_fairness": {
    "consistency_score": 0.92,
    "lipschitz_constant": 1.0,
    "sample_size": 1000,
    "violations": 80,
    "total_pairs": 499500,
    "status": "pass"
  }
}
```

## 3. Architecture — Metric Class Hierarchy

Based on the existing `FairnessWrapper` ABC in `src/faircheck/algorithms/base.py` and the CONTEXT.md decisions:

```
src/faircheck/analysis/
├── __init__.py          # Public API: BiasAnalyzer
├── engine.py            # BiasAnalyzer orchestrator class
├── metrics/
│   ├── __init__.py
│   ├── base.py          # BaseMetric ABC with threshold evaluation (D-03)
│   ├── demographic_parity.py
│   ├── equalized_odds.py
│   ├── disparate_impact.py
│   ├── predictive_parity.py
│   ├── calibration.py
│   └── individual_fairness.py
├── domains.py           # Hardcoded domain guidance dicts (D-01)
└── breakdown.py         # Per-group performance breakdown (BIAS-08)
```

### BaseMetric ABC Design

```python
class BaseMetric(ABC):
    """Each metric self-evaluates pass/fail/warning (D-03)."""
    
    name: str
    default_threshold: float
    
    @abstractmethod
    def compute(self, y_true, y_pred, sensitive_features, **kwargs) -> MetricResult:
        """Returns raw value + status."""
        
    def evaluate_status(self, value: float, threshold: float, warning_factor: float = 0.8) -> str:
        """Core threshold logic — co-located with each metric (D-03, D-05)."""
        # For metrics where lower is better (DPD, EOD, PP, Cal):
        if value <= threshold * warning_factor:
            return "pass"
        elif value <= threshold:
            return "warning"
        else:
            return "fail"
```

**Note:** Disparate Impact Ratio is inverted (higher is better, threshold ≥ 0.80). The `evaluate_status` method needs a `direction` parameter.

### MetricResult Dataclass

```python
@dataclass
class MetricResult:
    name: str
    value: float
    threshold: float
    status: str           # "pass" | "warning" | "fail"
    details: dict         # Metric-specific (e.g., per-group values)
    warning_message: str | None  # For small sample size (D-02)
```

## 4. Output JSON Structure (D-07)

Nested by protected attribute, per CONTEXT.md decision:

```json
{
  "protected_attributes": ["gender", "race"],
  "results": {
    "gender": {
      "metrics": {
        "demographic_parity_difference": {
          "value": 0.05,
          "threshold": 0.10,
          "status": "pass",
          "details": {
            "by_group": {"male": 0.72, "female": 0.67},
            "difference": 0.05
          }
        },
        "equalized_odds_difference": { ... },
        "disparate_impact_ratio": { ... },
        "predictive_parity": { ... },
        "calibration_by_group": { ... }
      },
      "performance_breakdown": {
        "male": {"accuracy": 0.85, "precision": 0.82, "recall": 0.78, "f1": 0.80},
        "female": {"accuracy": 0.83, "precision": 0.80, "recall": 0.76, "f1": 0.78}
      }
    },
    "race": { ... }
  },
  "individual_fairness": {
    "consistency_score": 0.92,
    "status": "pass",
    ...
  },
  "domain_guidance": {
    "domain": "hiring",
    "recommended_metrics": ["demographic_parity_difference", "disparate_impact_ratio"],
    "rationale": "Hiring contexts typically focus on selection rate parity..."
  },
  "overall_risk_level": "medium",
  "scan_metadata": {
    "timestamp": "...",
    "sample_size": 5000,
    "metrics_computed": 6
  }
}
```

**Note:** `individual_fairness` is at the top level (not nested under a protected attribute) because it's a cross-individual metric, not a group metric.

## 5. Domain Guidance Structure (D-01)

```python
DOMAIN_GUIDANCE = {
    "hiring": {
        "recommended_metrics": [
            "demographic_parity_difference",
            "disparate_impact_ratio",
        ],
        "critical_thresholds": {
            "disparate_impact_ratio": 0.80,  # EEOC 4/5ths rule
        },
        "rationale": "Employment law (US EEOC, EU AI Act Art. 10) focuses on selection rate parity. The 4/5ths rule requires disparate impact ratio ≥ 0.80.",
        "regulations": ["EEOC Guidelines", "EU AI Act Article 10"],
    },
    "lending": {
        "recommended_metrics": [
            "equalized_odds_difference",
            "predictive_parity",
        ],
        "critical_thresholds": {
            "equalized_odds_difference": 0.05,
        },
        "rationale": "Lending compliance (ECOA, EU AI Act) emphasizes equal error rates across groups to prevent systematically disadvantaging borrowers.",
        "regulations": ["ECOA", "EU AI Act Article 9"],
    },
    "healthcare": {
        "recommended_metrics": [
            "calibration_by_group",
            "equalized_odds_difference",
        ],
        "critical_thresholds": {
            "calibration_by_group": 0.03,
        },
        "rationale": "Healthcare AI (EU AI Act Art. 9) prioritizes calibration so predicted probabilities match actual outcomes across demographics.",
        "regulations": ["EU AI Act Article 9", "FDA AI/ML Guidelines"],
    },
}
```

## 6. Small Sample Size Handling (D-02)

**Minimum sample threshold:** 30 per subgroup (statistical convention for CLT).

**Implementation:**
```python
MIN_SUBGROUP_SIZE = 30

def compute_with_guard(self, group_data, ...):
    if len(group_data) < MIN_SUBGROUP_SIZE:
        return MetricResult(
            value=None,
            status="skipped",
            warning_message=f"Subgroup has {len(group_data)} samples (min: {MIN_SUBGROUP_SIZE}). Metric skipped."
        )
```

## 7. Integration with Existing Code

### Relationship to `src/faircheck/algorithms/`
The existing `FairnessWrapper` ABC in `algorithms/` is designed for **mitigation algorithms** (Phase 9: fit/predict/evaluate_fairness). Phase 3's `analysis/` module is separate — it's the **measurement engine** that computes metrics and returns results. The two are complementary:
- `analysis/` → measures bias (Phase 3)
- `algorithms/` → mitigates bias (Phase 9)

### Integration with IngestionPipeline
The `BiasAnalyzer` consumes the output of `IngestionPipeline.load()`:

```python
pipeline = IngestionPipeline()
result = pipeline.load("model.pkl", "data.csv")

analyzer = BiasAnalyzer(config=load_config())
analysis = analyzer.analyze(
    model=result.model,
    dataset=result.dataset,
    protected_attributes=["gender", "race"],
    domain="hiring",  # optional
)
```

### Config Integration
`config.py` already defines `DEFAULT_CONFIG` with `metrics.default_thresholds`. Phase 3 extends this with:
- `warning_factor` (default 0.8)
- `individual_fairness.lipschitz_constant` (default 1.0)
- `individual_fairness.sample_size` (default 1000)
- Per-metric threshold overrides

## 8. Validation Architecture

### Unit Testing Strategy
| Layer | What to Test | Approach |
|-------|-------------|----------|
| Individual metrics | Correctness against known values | Use standard benchmark datasets (German Credit, Adult Census) and compare against raw Fairlearn/AIF360 output |
| BaseMetric threshold logic | Pass/warning/fail boundaries | Parametrized tests with edge cases at exactly threshold, exactly warning boundary |
| BiasAnalyzer orchestration | Full pipeline produces valid JSON | Integration test with a simple synthetic dataset |
| Small sample guard | Warning + null for tiny groups | Synthetic dataset with one group having < 30 samples |
| Domain guidance | Correct recommendations | Unit tests checking each domain returns expected metrics |

### Benchmark Datasets
- **German Credit** (UCI): Binary classification, age/sex as protected attributes
- **Adult Census** (UCI): Binary classification, gender/race, well-established fairness benchmarks
- **Synthetic**: Controlled dataset for edge cases (perfectly fair model, maximally unfair model)

## 9. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| AIF360 sklearn API instability | Medium | Wrap all AIF360 calls behind our own functions; pin version |
| Individual fairness O(n²) on large data | High | Subsample with configurable `sample_size` parameter |
| Calibration metric ambiguity | Medium | Document exact ECE formula used; test against known calibration curves |
| Metric disagreement across libraries | Low | Use Fairlearn as primary, AIF360 only for metrics Fairlearn lacks |

---

*Phase: 03-bias-analysis-engine*
*Research completed: 2026-04-11*

---
phase: 03
plan: 2
title: "BiasAnalyzer Orchestrator, Per-Group Breakdown & Tests"
wave: 2
depends_on: [03-1]
files_modified:
  - src/faircheck/analysis/engine.py
  - src/faircheck/analysis/breakdown.py
  - src/faircheck/analysis/__init__.py
  - tests/analysis/__init__.py
  - tests/analysis/test_metrics.py
  - tests/analysis/test_engine.py
  - tests/analysis/test_domains.py
requirements: [BIAS-07, BIAS-08, BIAS-09]
autonomous: true
---

# Plan 03-2: BiasAnalyzer Orchestrator, Per-Group Breakdown & Tests

<objective>
Build the BiasAnalyzer orchestrator that runs all 6 metrics per protected attribute, produces the nested JSON output (D-07), integrates per-group performance breakdowns (BIAS-08), and includes domain guidance in results (BIAS-09). Add comprehensive tests validating correctness against known benchmark values.
</objective>

<must_haves>
- BiasAnalyzer.analyze() produces nested JSON keyed by protected attribute (D-07)
- Per-group breakdown includes accuracy, precision, recall, F1 per demographic subgroup (BIAS-08)
- Domain guidance is included in results when domain is specified (BIAS-09)
- Individual fairness result is at top level (not nested under a protected attribute)
- Metrics computed independently per protected attribute (D-06)
- Overall risk level derived from metric ensemble
- Tests verify metric correctness against known values
- Tests verify threshold pass/warning/fail boundaries
- Tests verify domain guidance returns correct recommendations
</must_haves>

## Tasks

<task id="03-2-1" title="Create per-group performance breakdown module">
<read_first>
- src/faircheck/analysis/metrics/base.py (MetricResult, BaseMetric)
- src/faircheck/ingestion/pipeline.py (IngestionResult structure)
</read_first>

<action>
Create `src/faircheck/analysis/breakdown.py`:

```python
"""Per-group performance breakdown (BIAS-08).

Computes accuracy, precision, recall, F1 for each demographic subgroup
using Fairlearn's MetricFrame.
"""

from __future__ import annotations

import functools

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def compute_performance_breakdown(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.Series,
) -> dict[str, dict[str, float]]:
    """Return per-group performance metrics.

    Returns
    -------
    dict
        Keyed by group name, each value is a dict with keys:
        ``accuracy``, ``precision``, ``recall``, ``f1``.
    """
    metrics = {
        "accuracy": accuracy_score,
        "precision": functools.partial(precision_score, zero_division=0),
        "recall": functools.partial(recall_score, zero_division=0),
        "f1": functools.partial(f1_score, zero_division=0),
    }

    mf = MetricFrame(
        metrics=metrics,
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive_features,
    )

    result: dict[str, dict[str, float]] = {}
    by_group = mf.by_group
    for group_name in by_group.index:
        result[str(group_name)] = {
            metric_name: float(by_group.loc[group_name, metric_name])
            for metric_name in metrics
        }

    return result
```
</action>

<acceptance_criteria>
- `breakdown.py` contains function `compute_performance_breakdown`
- Function returns a dict keyed by group name with nested dict containing `accuracy`, `precision`, `recall`, `f1`
- Uses `functools.partial(precision_score, zero_division=0)` to handle edge cases
- Uses `fairlearn.metrics.MetricFrame` for disaggregated computation
</acceptance_criteria>
</task>

<task id="03-2-2" title="Create BiasAnalyzer orchestrator engine">
<read_first>
- src/faircheck/analysis/metrics/__init__.py (all metric classes)
- src/faircheck/analysis/breakdown.py (performance breakdown)
- src/faircheck/analysis/domains.py (domain guidance)
- src/faircheck/config.py (DEFAULT_CONFIG and load_config)
- src/faircheck/ingestion/pipeline.py (IngestionResult, ModelAdapter, DatasetChunker)
</read_first>

<action>
Create `src/faircheck/analysis/engine.py`:

```python
"""BiasAnalyzer — orchestrates all fairness metrics for a scan.

Usage::

    from faircheck.analysis.engine import BiasAnalyzer
    from faircheck.config import load_config

    analyzer = BiasAnalyzer(config=load_config())
    results = analyzer.analyze(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features={"gender": gender_col, "race": race_col},
        y_prob=y_prob,          # optional
        feature_matrix=X_test,  # optional, for individual fairness
        domain="hiring",        # optional
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from faircheck.analysis.breakdown import compute_performance_breakdown
from faircheck.analysis.domains import get_domain_guidance
from faircheck.analysis.metrics import (
    CalibrationMetric,
    DemographicParityMetric,
    DisparateImpactMetric,
    EqualizedOddsMetric,
    IndividualFairnessMetric,
    MetricResult,
    PredictiveParityMetric,
)

logger = logging.getLogger(__name__)

# All group-level metrics (run per protected attribute)
_GROUP_METRICS = [
    DemographicParityMetric(),
    EqualizedOddsMetric(),
    DisparateImpactMetric(),
    PredictiveParityMetric(),
    CalibrationMetric(),
]

# Global metric (not per-attribute)
_INDIVIDUAL_METRIC = IndividualFairnessMetric()


@dataclass
class AnalysisResult:
    """Full bias analysis output — serializable to JSON."""

    protected_attributes: list[str]
    results: dict[str, dict[str, Any]]
    individual_fairness: dict[str, Any] | None
    domain_guidance: dict[str, Any] | None
    overall_risk_level: str
    scan_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "protected_attributes": self.protected_attributes,
            "results": self.results,
            "individual_fairness": self.individual_fairness,
            "domain_guidance": self.domain_guidance,
            "overall_risk_level": self.overall_risk_level,
            "scan_metadata": self.scan_metadata,
        }


class BiasAnalyzer:
    """Orchestrates all fairness metrics across protected attributes."""

    def __init__(self, config: dict | None = None) -> None:
        from faircheck.config import DEFAULT_CONFIG

        self.config = config or DEFAULT_CONFIG

    def analyze(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: dict[str, pd.Series],
        y_prob: np.ndarray | None = None,
        feature_matrix: np.ndarray | pd.DataFrame | None = None,
        domain: str | None = None,
    ) -> AnalysisResult:
        """Run all metrics for each protected attribute.

        Parameters
        ----------
        y_true : array-like
            Ground truth labels.
        y_pred : array-like
            Model predictions.
        sensitive_features : dict[str, Series]
            Mapping of attribute name → column values.
        y_prob : array-like, optional
            Predicted probabilities (for calibration + individual fairness).
        feature_matrix : array-like, optional
            Non-protected features for individual fairness.
        domain : str, optional
            Domain for guidance (``"hiring"``, ``"lending"``, ``"healthcare"``).
        """
        thresholds = self.config.get("metrics", {}).get("default_thresholds", {})
        warning_factor = self.config.get("metrics", {}).get("warning_factor", 0.8)
        if_config = self.config.get("individual_fairness", {})

        attr_names = list(sensitive_features.keys())
        per_attr_results: dict[str, dict[str, Any]] = {}

        for attr_name, attr_values in sensitive_features.items():
            attr_values = pd.Series(attr_values)
            metrics_out: dict[str, Any] = {}

            for metric in _GROUP_METRICS:
                threshold = thresholds.get(metric.name, metric.default_threshold)
                kwargs: dict[str, Any] = {}
                if metric.name == "calibration_by_group":
                    kwargs["y_prob"] = y_prob

                result = metric.compute(
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_features=attr_values,
                    threshold=threshold,
                    warning_factor=warning_factor,
                    **kwargs,
                )
                metrics_out[metric.name] = _result_to_dict(result)

            breakdown = compute_performance_breakdown(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=attr_values,
            )

            per_attr_results[attr_name] = {
                "metrics": metrics_out,
                "performance_breakdown": breakdown,
            }

        # Individual fairness (global, not per-attribute)
        if_result_dict = None
        if feature_matrix is not None and y_prob is not None:
            if_threshold = thresholds.get(
                _INDIVIDUAL_METRIC.name, _INDIVIDUAL_METRIC.default_threshold
            )
            if_result = _INDIVIDUAL_METRIC.compute(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=pd.Series(dtype=object),  # not used
                threshold=if_threshold,
                warning_factor=warning_factor,
                y_prob=y_prob,
                feature_matrix=feature_matrix,
                lipschitz_constant=if_config.get("lipschitz_constant", 1.0),
                sample_size=if_config.get("sample_size", 1000),
            )
            if_result_dict = _result_to_dict(if_result)

        # Domain guidance
        guidance = get_domain_guidance(domain)
        guidance_dict = dict(guidance) if guidance else None
        if guidance_dict and domain:
            guidance_dict["domain"] = domain

        # Overall risk level
        risk = self._compute_risk_level(per_attr_results, if_result_dict)

        metrics_computed = len(_GROUP_METRICS) * len(attr_names)
        if if_result_dict:
            metrics_computed += 1

        return AnalysisResult(
            protected_attributes=attr_names,
            results=per_attr_results,
            individual_fairness=if_result_dict,
            domain_guidance=guidance_dict,
            overall_risk_level=risk,
            scan_metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sample_size": len(y_true),
                "metrics_computed": metrics_computed,
            },
        )

    @staticmethod
    def _compute_risk_level(
        per_attr: dict[str, dict[str, Any]],
        individual: dict[str, Any] | None,
    ) -> str:
        statuses: list[str] = []
        for attr_data in per_attr.values():
            for metric_data in attr_data.get("metrics", {}).values():
                s = metric_data.get("status")
                if s:
                    statuses.append(s)
        if individual:
            s = individual.get("status")
            if s:
                statuses.append(s)

        if any(s == "fail" for s in statuses):
            return "high"
        if any(s == "warning" for s in statuses):
            return "medium"
        return "low"


def _result_to_dict(r: MetricResult) -> dict[str, Any]:
    return {
        "name": r.name,
        "value": r.value,
        "threshold": r.threshold,
        "status": r.status,
        "details": r.details,
        "warning_message": r.warning_message,
    }
```

Update `src/faircheck/analysis/__init__.py` to export the public API:

```python
from faircheck.analysis.engine import AnalysisResult, BiasAnalyzer
from faircheck.analysis.breakdown import compute_performance_breakdown
from faircheck.analysis.domains import get_domain_guidance, list_supported_domains

__all__ = [
    "AnalysisResult",
    "BiasAnalyzer",
    "compute_performance_breakdown",
    "get_domain_guidance",
    "list_supported_domains",
]
```
</action>

<acceptance_criteria>
- `engine.py` contains `class BiasAnalyzer` with `analyze()` method
- `engine.py` contains `class AnalysisResult` with `to_dict()` method
- `BiasAnalyzer.analyze()` accepts `sensitive_features` as `dict[str, pd.Series]`
- Results are nested by protected attribute name (D-07)
- Individual fairness result is at top level, not nested under an attribute
- `_compute_risk_level` returns `"high"` if any metric fails, `"medium"` if any warns, `"low"` otherwise
- `src/faircheck/analysis/__init__.py` exports `BiasAnalyzer`, `AnalysisResult`, `compute_performance_breakdown`, `get_domain_guidance`, `list_supported_domains`
</acceptance_criteria>
</task>

<task id="03-2-3" title="Write unit tests for individual metrics">
<read_first>
- src/faircheck/analysis/metrics/demographic_parity.py
- src/faircheck/analysis/metrics/equalized_odds.py
- src/faircheck/analysis/metrics/disparate_impact.py
- src/faircheck/analysis/metrics/predictive_parity.py
- src/faircheck/analysis/metrics/calibration.py
- src/faircheck/analysis/metrics/individual_fairness.py
- src/faircheck/analysis/metrics/base.py
- tests/api/test_health.py (existing test patterns)
</read_first>

<action>
Create `tests/analysis/__init__.py` (empty).

Create `tests/analysis/test_metrics.py`:

```python
"""Tests for individual fairness metric classes.

Uses a small synthetic dataset where results are manually verifiable.
"""

import numpy as np
import pandas as pd
import pytest

from faircheck.analysis.metrics import (
    CalibrationMetric,
    DemographicParityMetric,
    DisparateImpactMetric,
    EqualizedOddsMetric,
    IndividualFairnessMetric,
    PredictiveParityMetric,
)
from faircheck.analysis.metrics.base import BaseMetric, MetricResult


# ─── Fixtures ───────────────────────────────────────────────

@pytest.fixture
def synthetic_data():
    """Simple synthetic binary classification data with known bias."""
    # 100 samples: 50 male, 50 female
    # Model is biased: higher selection rate for males
    rng = np.random.default_rng(42)
    n = 100
    gender = pd.Series(["male"] * 50 + ["female"] * 50)
    y_true = np.array([1] * 30 + [0] * 20 + [1] * 30 + [0] * 20)
    # Males: predict 25/30 positives correctly, 5/20 false positives
    # Females: predict 20/30 positives correctly, 2/20 false positives
    y_pred_male = np.array([1] * 25 + [0] * 5 + [1] * 5 + [0] * 15)
    y_pred_female = np.array([1] * 20 + [0] * 10 + [1] * 2 + [0] * 18)
    y_pred = np.concatenate([y_pred_male, y_pred_female])
    y_prob = rng.uniform(0.3, 0.9, size=n)
    X_features = rng.standard_normal((n, 5))
    return {
        "y_true": y_true,
        "y_pred": y_pred,
        "gender": gender,
        "y_prob": y_prob,
        "X_features": X_features,
    }


# ─── BaseMetric threshold tests ────────────────────────────

class TestEvaluateStatus:
    def test_lower_is_better_pass(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.05, threshold=0.10, warning_factor=0.8) == "pass"

    def test_lower_is_better_warning(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.09, threshold=0.10, warning_factor=0.8) == "warning"

    def test_lower_is_better_fail(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.15, threshold=0.10, warning_factor=0.8) == "fail"

    def test_higher_is_better_pass(self):
        m = DisparateImpactMetric()
        assert m.evaluate_status(0.95, threshold=0.80, warning_factor=0.8) == "pass"

    def test_higher_is_better_warning(self):
        m = DisparateImpactMetric()
        assert m.evaluate_status(0.85, threshold=0.80, warning_factor=0.8) == "warning"

    def test_higher_is_better_fail(self):
        m = DisparateImpactMetric()
        assert m.evaluate_status(0.70, threshold=0.80, warning_factor=0.8) == "fail"


# ─── Demographic Parity ────────────────────────────────────

class TestDemographicParity:
    def test_returns_metric_result(self, synthetic_data):
        metric = DemographicParityMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
        )
        assert isinstance(result, MetricResult)
        assert result.name == "demographic_parity_difference"
        assert result.value is not None
        assert result.status in ("pass", "warning", "fail")
        assert "by_group" in result.details

    def test_perfect_parity_passes(self):
        y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        sf = pd.Series(["a", "a", "a", "a", "b", "b", "b", "b"])
        metric = DemographicParityMetric()
        result = metric.compute(y_true, y_pred, sf)
        assert abs(result.value) < 0.01
        assert result.status == "pass"


# ─── Equalized Odds ────────────────────────────────────────

class TestEqualizedOdds:
    def test_returns_metric_result(self, synthetic_data):
        metric = EqualizedOddsMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
        )
        assert isinstance(result, MetricResult)
        assert result.name == "equalized_odds_difference"
        assert "tpr_difference" in result.details
        assert "fpr_difference" in result.details


# ─── Disparate Impact ──────────────────────────────────────

class TestDisparateImpact:
    def test_returns_ratio(self, synthetic_data):
        metric = DisparateImpactMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
        )
        assert isinstance(result, MetricResult)
        assert result.name == "disparate_impact_ratio"
        assert result.value is not None
        assert 0.0 <= result.value <= 1.0


# ─── Predictive Parity ─────────────────────────────────────

class TestPredictiveParity:
    def test_returns_precision_diff(self, synthetic_data):
        metric = PredictiveParityMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
        )
        assert isinstance(result, MetricResult)
        assert result.name == "predictive_parity"
        assert "by_group" in result.details


# ─── Calibration ───────────────────────────────────────────

class TestCalibration:
    def test_skips_without_probs(self, synthetic_data):
        metric = CalibrationMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
        )
        assert result.status == "skipped"

    def test_computes_with_probs(self, synthetic_data):
        metric = CalibrationMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
            y_prob=synthetic_data["y_prob"],
        )
        assert isinstance(result, MetricResult)
        assert result.name == "calibration_by_group"


# ─── Individual Fairness ───────────────────────────────────

class TestIndividualFairness:
    def test_skips_without_features(self, synthetic_data):
        metric = IndividualFairnessMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
            y_prob=synthetic_data["y_prob"],
        )
        assert result.status == "skipped"

    def test_computes_consistency(self, synthetic_data):
        metric = IndividualFairnessMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
            y_prob=synthetic_data["y_prob"],
            feature_matrix=synthetic_data["X_features"],
            sample_size=50,
        )
        assert isinstance(result, MetricResult)
        assert result.value is not None
        assert 0.0 <= result.value <= 1.0
        assert "consistency_score" in result.details
        assert "violations" in result.details
```
</action>

<acceptance_criteria>
- `tests/analysis/__init__.py` exists
- `tests/analysis/test_metrics.py` contains test classes for all 6 metrics
- `TestEvaluateStatus` tests pass/warning/fail boundaries for both `higher_is_better=False` and `higher_is_better=True`
- `TestCalibration.test_skips_without_probs` asserts `status == "skipped"`
- `TestIndividualFairness.test_skips_without_features` asserts `status == "skipped"`
- Running `pytest tests/analysis/test_metrics.py` exits 0
</acceptance_criteria>
</task>

<task id="03-2-4" title="Write integration tests for BiasAnalyzer and domain guidance">
<read_first>
- src/faircheck/analysis/engine.py (BiasAnalyzer)
- src/faircheck/analysis/domains.py (domain guidance)
- tests/analysis/test_metrics.py (synthetic_data fixture to reuse)
</read_first>

<action>
Create `tests/analysis/test_engine.py`:

```python
"""Integration tests for BiasAnalyzer orchestrator."""

import numpy as np
import pandas as pd
import pytest

from faircheck.analysis.engine import AnalysisResult, BiasAnalyzer
from faircheck.config import DEFAULT_CONFIG


@pytest.fixture
def analyzer():
    return BiasAnalyzer(config=DEFAULT_CONFIG)


@pytest.fixture
def sample_data():
    rng = np.random.default_rng(42)
    n = 200
    gender = pd.Series(["male"] * 100 + ["female"] * 100)
    race = pd.Series((["white"] * 50 + ["black"] * 50) * 2)
    y_true = rng.integers(0, 2, size=n)
    y_pred = rng.integers(0, 2, size=n)
    y_prob = rng.uniform(0.1, 0.9, size=n)
    X = rng.standard_normal((n, 4))
    return {
        "y_true": y_true,
        "y_pred": y_pred,
        "sensitive_features": {"gender": gender, "race": race},
        "y_prob": y_prob,
        "X": X,
    }


class TestBiasAnalyzer:
    def test_analyze_returns_result(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        assert isinstance(result, AnalysisResult)
        assert result.protected_attributes == ["gender", "race"]
        assert "gender" in result.results
        assert "race" in result.results

    def test_nested_structure(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        gender_data = result.results["gender"]
        assert "metrics" in gender_data
        assert "performance_breakdown" in gender_data
        assert "demographic_parity_difference" in gender_data["metrics"]
        assert "equalized_odds_difference" in gender_data["metrics"]
        assert "disparate_impact_ratio" in gender_data["metrics"]
        assert "predictive_parity" in gender_data["metrics"]

    def test_performance_breakdown(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        breakdown = result.results["gender"]["performance_breakdown"]
        assert "male" in breakdown
        assert "female" in breakdown
        for group_metrics in breakdown.values():
            assert "accuracy" in group_metrics
            assert "precision" in group_metrics
            assert "recall" in group_metrics
            assert "f1" in group_metrics

    def test_individual_fairness_included(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
            y_prob=sample_data["y_prob"],
            feature_matrix=sample_data["X"],
        )
        assert result.individual_fairness is not None
        assert "consistency_score" in result.individual_fairness.get("details", {})

    def test_individual_fairness_none_without_probs(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        assert result.individual_fairness is None

    def test_domain_guidance_included(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
            domain="hiring",
        )
        assert result.domain_guidance is not None
        assert result.domain_guidance["domain"] == "hiring"
        assert "recommended_metrics" in result.domain_guidance

    def test_domain_guidance_none_without_domain(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        assert result.domain_guidance is None

    def test_risk_level_computed(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        assert result.overall_risk_level in ("high", "medium", "low")

    def test_to_dict(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "protected_attributes" in d
        assert "results" in d
        assert "overall_risk_level" in d
        assert "scan_metadata" in d

    def test_scan_metadata(self, analyzer, sample_data):
        result = analyzer.analyze(
            y_true=sample_data["y_true"],
            y_pred=sample_data["y_pred"],
            sensitive_features=sample_data["sensitive_features"],
        )
        assert "timestamp" in result.scan_metadata
        assert result.scan_metadata["sample_size"] == 200
        assert result.scan_metadata["metrics_computed"] > 0


Create `tests/analysis/test_domains.py`:

```python
"""Tests for domain guidance module."""

from faircheck.analysis.domains import (
    DOMAIN_GUIDANCE,
    get_domain_guidance,
    list_supported_domains,
)


class TestDomainGuidance:
    def test_hiring_guidance(self):
        g = get_domain_guidance("hiring")
        assert g is not None
        assert "demographic_parity_difference" in g["recommended_metrics"]
        assert "disparate_impact_ratio" in g["recommended_metrics"]

    def test_lending_guidance(self):
        g = get_domain_guidance("lending")
        assert g is not None
        assert "equalized_odds_difference" in g["recommended_metrics"]

    def test_healthcare_guidance(self):
        g = get_domain_guidance("healthcare")
        assert g is not None
        assert "calibration_by_group" in g["recommended_metrics"]

    def test_unknown_domain_returns_none(self):
        assert get_domain_guidance("unknown") is None

    def test_none_domain_returns_none(self):
        assert get_domain_guidance(None) is None

    def test_case_insensitive(self):
        assert get_domain_guidance("HIRING") is not None
        assert get_domain_guidance("Lending") is not None

    def test_list_supported(self):
        domains = list_supported_domains()
        assert "hiring" in domains
        assert "lending" in domains
        assert "healthcare" in domains
        assert len(domains) == 3
```
</action>

<acceptance_criteria>
- `tests/analysis/test_engine.py` contains `TestBiasAnalyzer` class with at least 10 test methods
- `tests/analysis/test_domains.py` contains `TestDomainGuidance` class with 7 test methods
- `test_nested_structure` checks all 4 group metrics are present under `results["gender"]["metrics"]`
- `test_performance_breakdown` checks accuracy/precision/recall/f1 per group
- `test_domain_guidance_included` checks guidance dict includes `domain` and `recommended_metrics`
- Running `pytest tests/analysis/` exits 0
</acceptance_criteria>
</task>

<verification>
After all tasks complete:
1. `python -c "from faircheck.analysis import BiasAnalyzer; print('OK')"` exits 0
2. `pytest tests/analysis/ -v` exits 0 with all tests passing
3. `pytest tests/ -v` exits 0 (no regressions in existing tests)
</verification>

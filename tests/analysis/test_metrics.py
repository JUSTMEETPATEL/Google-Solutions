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
from faircheck.analysis.metrics.base import MetricResult


# ─── Fixtures ───────────────────────────────────────────────


@pytest.fixture
def synthetic_data():
    """Simple synthetic binary classification data with known bias.

    100 samples: 50 male, 50 female.
    Model is biased — higher selection rate for males.
    """
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
    """Verify threshold pass/warning/fail boundaries for both directions."""

    def test_lower_is_better_pass(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.05, threshold=0.10, warning_factor=0.8) == "pass"

    def test_lower_is_better_warning(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.09, threshold=0.10, warning_factor=0.8) == "warning"

    def test_lower_is_better_fail(self):
        m = DemographicParityMetric()
        assert m.evaluate_status(0.15, threshold=0.10, warning_factor=0.8) == "fail"

    def test_lower_is_better_exact_boundary(self):
        m = DemographicParityMetric()
        # Exactly at warning_bound (0.08) → pass
        assert m.evaluate_status(0.08, threshold=0.10, warning_factor=0.8) == "pass"
        # Exactly at threshold (0.10) → warning
        assert m.evaluate_status(0.10, threshold=0.10, warning_factor=0.8) == "warning"

    def test_higher_is_better_pass(self):
        m = DisparateImpactMetric()
        assert m.evaluate_status(0.95, threshold=0.80, warning_factor=0.8) == "pass"

    def test_higher_is_better_warning(self):
        m = DisparateImpactMetric()
        # warning_bound = 0.80 + 0.20 * 0.20 = 0.84
        assert m.evaluate_status(0.82, threshold=0.80, warning_factor=0.8) == "warning"

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

    def test_single_group_skips(self):
        metric = DisparateImpactMetric()
        y_true = np.array([1, 0, 1, 0])
        y_pred = np.array([1, 0, 0, 0])
        sf = pd.Series(["a", "a", "a", "a"])
        result = metric.compute(y_true, y_pred, sf)
        assert result.status == "skipped"


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

    def test_skips_without_probs(self, synthetic_data):
        metric = IndividualFairnessMetric()
        result = metric.compute(
            y_true=synthetic_data["y_true"],
            y_pred=synthetic_data["y_pred"],
            sensitive_features=synthetic_data["gender"],
            feature_matrix=synthetic_data["X_features"],
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
        assert "total_pairs" in result.details

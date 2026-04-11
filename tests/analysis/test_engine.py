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
    """200-sample dataset with two protected attributes."""
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

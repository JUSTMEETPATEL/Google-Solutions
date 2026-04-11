"""Tests for mitigation pipeline and all 6 algorithms."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from faircheck.mitigation import MitigationPipeline, list_algorithms, get_algorithm
from faircheck.mitigation.base import MitigationResult
from faircheck.mitigation.reweighing import ReweighingMitigation
from faircheck.mitigation.disparate_impact_remover import DisparateImpactRemoverMitigation
from faircheck.mitigation.adversarial_debiasing import AdversarialDebiasingMitigation
from faircheck.mitigation.equalized_odds import EqualizedOddsPostProcessing
from faircheck.mitigation.calibrated_eq_odds import CalibratedEqualizedOdds
from faircheck.mitigation.reject_option import RejectOptionClassification


@pytest.fixture
def biased_dataset():
    """Synthetic biased dataset: model favors group A over group B."""
    rng = np.random.default_rng(42)
    n = 200

    # Features
    X = rng.standard_normal((n, 4))
    gender = pd.Series(["male"] * 100 + ["female"] * 100)
    y = np.concatenate([
        rng.choice([0, 1], p=[0.3, 0.7], size=100),  # males: 70% positive
        rng.choice([0, 1], p=[0.6, 0.4], size=100),  # females: 40% positive
    ])

    # Train/test split (MIT-08)
    split = 150
    return {
        "X_train": X[:split],
        "y_train": y[:split],
        "X_test": X[split:],
        "y_test": y[split:],
        "sensitive_train": gender[:split],
        "sensitive_test": gender[split:],
        "gender_full": gender,
    }


# ─── Algorithm Registry ────────────────────────────────────


class TestAlgorithmRegistry:
    def test_list_algorithms(self):
        algos = list_algorithms()
        assert len(algos) == 6
        names = {a["name"] for a in algos}
        assert "reweighing" in names
        assert "disparate_impact_remover" in names
        assert "adversarial_debiasing" in names
        assert "equalized_odds_postprocessing" in names
        assert "calibrated_equalized_odds" in names
        assert "reject_option_classification" in names

    def test_get_algorithm(self):
        algo = get_algorithm("reweighing")
        assert isinstance(algo, ReweighingMitigation)

    def test_get_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown algorithm"):
            get_algorithm("nonexistent")


# ─── Individual Algorithms ─────────────────────────────────


class TestReweighing:
    def test_produces_weights(self, biased_dataset):
        algo = ReweighingMitigation()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        assert "sample_weight" in result
        assert len(result["sample_weight"]) == len(biased_dataset["y_train"])
        assert np.all(result["sample_weight"] > 0)

    def test_does_not_modify_test(self, biased_dataset):
        algo = ReweighingMitigation()
        X_test_before = biased_dataset["X_test"].copy()
        algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        np.testing.assert_array_equal(biased_dataset["X_test"], X_test_before)


class TestDisparateImpactRemover:
    def test_transforms_features(self, biased_dataset):
        algo = DisparateImpactRemoverMitigation()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        assert "X_train_transformed" in result
        assert result["X_train_transformed"].shape == biased_dataset["X_train"].shape


class TestAdversarialDebiasing:
    def test_produces_predictions(self, biased_dataset):
        algo = AdversarialDebiasingMitigation()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        assert "model" in result
        assert "y_pred_test" in result
        assert len(result["y_pred_test"]) == len(biased_dataset["y_test"])


class TestEqualizedOddsPostProcessing:
    def test_adjusts_predictions(self, biased_dataset):
        algo = EqualizedOddsPostProcessing()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        assert "y_pred_adjusted" in result
        assert len(result["y_pred_adjusted"]) == len(biased_dataset["y_test"])


class TestCalibratedEqualizedOdds:
    def test_adjusts_predictions(self, biased_dataset):
        algo = CalibratedEqualizedOdds()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
        )
        assert "y_pred_adjusted" in result


class TestRejectOption:
    def test_adjusts_borderline(self, biased_dataset):
        rng = np.random.default_rng(42)
        probs = rng.uniform(0.3, 0.7, size=len(biased_dataset["y_test"]))

        algo = RejectOptionClassification()
        result = algo.apply(
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_feature="gender",
            sensitive_train=biased_dataset["sensitive_train"],
            sensitive_test=biased_dataset["sensitive_test"],
            y_prob_test=probs,
        )
        assert "y_pred_adjusted" in result
        assert "samples_adjusted" in result
        assert result["samples_adjusted"] >= 0

    def test_requires_probs(self, biased_dataset):
        algo = RejectOptionClassification()
        with pytest.raises(ValueError, match="probability scores"):
            algo.apply(
                X_train=biased_dataset["X_train"],
                y_train=biased_dataset["y_train"],
                X_test=biased_dataset["X_test"],
                y_test=biased_dataset["y_test"],
                sensitive_feature="gender",
                sensitive_train=biased_dataset["sensitive_train"],
                sensitive_test=biased_dataset["sensitive_test"],
            )


# ─── Pipeline Integration ──────────────────────────────────


class TestMitigationPipeline:
    def test_run_reweighing(self, biased_dataset):
        pipeline = MitigationPipeline()
        result = pipeline.run(
            algorithm="reweighing",
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_features={
                "gender": (biased_dataset["sensitive_train"], biased_dataset["sensitive_test"]),
            },
        )
        assert isinstance(result, MitigationResult)
        assert result.success is True
        assert result.algorithm == "reweighing"
        assert result.before_metrics != {}
        assert result.after_metrics != {}

    def test_before_after_comparison(self, biased_dataset):
        pipeline = MitigationPipeline()
        result = pipeline.run(
            algorithm="equalized_odds_postprocessing",
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_features={
                "gender": (biased_dataset["sensitive_train"], biased_dataset["sensitive_test"]),
            },
        )
        assert "results" in result.before_metrics
        assert "results" in result.after_metrics
        # Both should have "gender" attribute results
        assert "gender" in result.before_metrics["results"]
        assert "gender" in result.after_metrics["results"]

    def test_to_dict(self, biased_dataset):
        pipeline = MitigationPipeline()
        result = pipeline.run(
            algorithm="reweighing",
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_features={
                "gender": (biased_dataset["sensitive_train"], biased_dataset["sensitive_test"]),
            },
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["algorithm"] == "reweighing"
        assert d["success"] is True

    def test_train_test_split_enforced(self, biased_dataset):
        """MIT-08: test data must not be modified."""
        X_test_before = biased_dataset["X_test"].copy()
        y_test_before = biased_dataset["y_test"].copy()

        pipeline = MitigationPipeline()
        pipeline.run(
            algorithm="disparate_impact_remover",
            X_train=biased_dataset["X_train"],
            y_train=biased_dataset["y_train"],
            X_test=biased_dataset["X_test"],
            y_test=biased_dataset["y_test"],
            sensitive_features={
                "gender": (biased_dataset["sensitive_train"], biased_dataset["sensitive_test"]),
            },
        )
        np.testing.assert_array_equal(biased_dataset["X_test"], X_test_before)
        np.testing.assert_array_equal(biased_dataset["y_test"], y_test_before)

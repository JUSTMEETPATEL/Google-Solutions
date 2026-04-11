"""Mitigation Pipeline — orchestrates algorithm application with before/after comparison (MIT-07)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from faircheck.analysis.engine import BiasAnalyzer
from faircheck.mitigation.base import BaseMitigation, MitigationResult

logger = logging.getLogger(__name__)

# Registry of available algorithms
_ALGORITHMS: dict[str, type[BaseMitigation]] = {}


def register_algorithm(cls: type[BaseMitigation]) -> type[BaseMitigation]:
    """Register a mitigation algorithm by name."""
    _ALGORITHMS[cls.name] = cls
    return cls


def get_algorithm(name: str) -> BaseMitigation:
    """Get a registered algorithm instance by name."""
    if name not in _ALGORITHMS:
        available = ", ".join(sorted(_ALGORITHMS.keys()))
        raise ValueError(
            f"Unknown algorithm '{name}'. Available: {available}"
        )
    return _ALGORITHMS[name]()


def list_algorithms() -> list[dict[str, str]]:
    """List all registered mitigation algorithms."""
    return [
        {"name": cls.name, "category": cls.category}
        for cls in _ALGORITHMS.values()
    ]


class MitigationPipeline:
    """Orchestrates mitigation with before/after bias comparison (MIT-07).

    Usage::

        pipeline = MitigationPipeline()
        result = pipeline.run(
            algorithm="reweighing",
            X_train=X_train, y_train=y_train,
            X_test=X_test, y_test=y_test,
            sensitive_features={"gender": (train_gender, test_gender)},
        )
    """

    def __init__(self, config: dict | None = None) -> None:
        from faircheck.config import DEFAULT_CONFIG
        self.config = config or DEFAULT_CONFIG
        self.analyzer = BiasAnalyzer(config=self.config)

    def run(
        self,
        algorithm: str,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray | pd.DataFrame,
        y_test: np.ndarray,
        sensitive_features: dict[str, tuple[pd.Series, pd.Series]],
        y_pred_before: np.ndarray | None = None,
        estimator: Any = None,
        **kwargs: Any,
    ) -> MitigationResult:
        """Apply mitigation and compute before/after metrics.

        Parameters
        ----------
        algorithm : str
            Name of the mitigation algorithm.
        X_train, y_train : array-like
            Training data (mitigation applied here only — MIT-08).
        X_test, y_test : array-like
            Test data (NEVER modified).
        sensitive_features : dict
            Mapping of attribute name → (train_series, test_series).
        y_pred_before : array-like, optional
            Original model predictions on test set. If None, uses a
            LogisticRegression fit on training data.
        estimator : estimator, optional
            Fitted sklearn estimator for post-processing algorithms.

        Returns
        -------
        MitigationResult
            Contains before/after metrics comparison.
        """
        algo = get_algorithm(algorithm)

        # Use first sensitive feature for mitigation
        first_attr = next(iter(sensitive_features))
        sensitive_train, sensitive_test = sensitive_features[first_attr]

        # Get original predictions if not provided
        if y_pred_before is None:
            from sklearn.linear_model import LogisticRegression
            est = LogisticRegression(max_iter=1000, solver="lbfgs")
            est.fit(np.asarray(X_train), np.asarray(y_train))
            y_pred_before = est.predict(np.asarray(X_test))
            if estimator is None:
                estimator = est

        # Compute BEFORE metrics
        before_sf = {attr: s[1] for attr, s in sensitive_features.items()}
        before_analysis = self.analyzer.analyze(
            y_true=np.asarray(y_test),
            y_pred=np.asarray(y_pred_before),
            sensitive_features=before_sf,
        )
        before_metrics = before_analysis.to_dict()

        # Apply mitigation
        try:
            result = algo.apply(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                sensitive_feature=first_attr,
                sensitive_train=sensitive_train,
                sensitive_test=sensitive_test,
                estimator=estimator,
                **kwargs,
            )
        except Exception as e:
            logger.error("Mitigation '%s' failed: %s", algorithm, e)
            return MitigationResult(
                algorithm=algorithm,
                category=algo.category,
                success=False,
                before_metrics=before_metrics,
                error=str(e),
            )

        # Get after predictions
        if "y_pred_adjusted" in result:
            y_pred_after = result["y_pred_adjusted"]
        elif "y_pred_test" in result:
            y_pred_after = result["y_pred_test"]
        elif "model" in result:
            y_pred_after = result["model"].predict(np.asarray(X_test))
        elif "sample_weight" in result:
            # Re-train with weights and predict
            from sklearn.linear_model import LogisticRegression
            retrained = LogisticRegression(max_iter=1000, solver="lbfgs")
            retrained.fit(
                np.asarray(X_train), np.asarray(y_train),
                sample_weight=result["sample_weight"],
            )
            y_pred_after = retrained.predict(np.asarray(X_test))
        else:
            y_pred_after = y_pred_before  # Fallback

        # Compute AFTER metrics
        after_analysis = self.analyzer.analyze(
            y_true=np.asarray(y_test),
            y_pred=np.asarray(y_pred_after),
            sensitive_features=before_sf,
        )
        after_metrics = after_analysis.to_dict()

        return MitigationResult(
            algorithm=algorithm,
            category=algo.category,
            success=True,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            details={k: v for k, v in result.items() if k not in ("model", "postprocessor")},
        )


# Auto-register all algorithms
def _register_all() -> None:
    from faircheck.mitigation.reweighing import ReweighingMitigation
    from faircheck.mitigation.disparate_impact_remover import DisparateImpactRemoverMitigation
    from faircheck.mitigation.adversarial_debiasing import AdversarialDebiasingMitigation
    from faircheck.mitigation.equalized_odds import EqualizedOddsPostProcessing
    from faircheck.mitigation.calibrated_eq_odds import CalibratedEqualizedOdds
    from faircheck.mitigation.reject_option import RejectOptionClassification

    for cls in [
        ReweighingMitigation,
        DisparateImpactRemoverMitigation,
        AdversarialDebiasingMitigation,
        EqualizedOddsPostProcessing,
        CalibratedEqualizedOdds,
        RejectOptionClassification,
    ]:
        register_algorithm(cls)


_register_all()

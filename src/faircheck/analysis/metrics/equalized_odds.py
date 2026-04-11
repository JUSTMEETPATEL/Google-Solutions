"""Equalized Odds Difference metric (BIAS-02)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    equalized_odds_difference,
    false_positive_rate,
    true_positive_rate,
)

from .base import BaseMetric, MetricResult


class EqualizedOddsMetric(BaseMetric):
    """Measures max of TPR difference and FPR difference across groups.

    A value of 0 means perfect equalized odds. Default threshold ≤ 0.10.
    """

    name = "equalized_odds_difference"
    default_threshold = 0.10
    higher_is_better = False

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs: Any,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        value = equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )

        mf = MetricFrame(
            metrics={"tpr": true_positive_rate, "fpr": false_positive_rate},
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        by_group = mf.by_group.to_dict()

        status = self.evaluate_status(abs(value), threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "tpr_difference": float(mf.difference()["tpr"]),
                "fpr_difference": float(mf.difference()["fpr"]),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )

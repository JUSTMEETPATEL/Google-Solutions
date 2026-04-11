"""Demographic Parity Difference metric (BIAS-01)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame, demographic_parity_difference, selection_rate

from .base import BaseMetric, MetricResult


class DemographicParityMetric(BaseMetric):
    """Measures difference in selection rates across groups.

    A value of 0 means perfect parity. Default threshold ≤ 0.10.
    """

    name = "demographic_parity_difference"
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

        value = demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )

        # Per-group selection rates
        mf = MetricFrame(
            metrics=selection_rate,
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
                "difference": float(abs(value)),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )

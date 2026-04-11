"""Predictive Parity metric (BIAS-04)."""

from __future__ import annotations

import functools
from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame
from sklearn.metrics import precision_score

from .base import BaseMetric, MetricResult


class PredictiveParityMetric(BaseMetric):
    """Measures max difference in precision (PPV) across groups.

    A value of 0 means perfect predictive parity.  Default threshold ≤ 0.10.
    """

    name = "predictive_parity"
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

        precision_fn = functools.partial(precision_score, zero_division=0)
        mf = MetricFrame(
            metrics=precision_fn,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )

        by_group = mf.by_group.to_dict()
        value = float(mf.difference())

        status = self.evaluate_status(abs(value), threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=value,
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

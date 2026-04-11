"""Disparate Impact Ratio metric (BIAS-03)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame, selection_rate

from .base import BaseMetric, MetricResult


class DisparateImpactMetric(BaseMetric):
    """Ratio of favorable outcome rates between groups.

    A value of 1.0 means perfect parity.  Default threshold ≥ 0.80
    (the EEOC 4/5ths rule).  ``higher_is_better`` is ``True``.
    """

    name = "disparate_impact_ratio"
    default_threshold = 0.80
    higher_is_better = True

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

        mf = MetricFrame(
            metrics=selection_rate,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        by_group = mf.by_group.to_dict()
        group_rates = list(by_group.values())

        if len(group_rates) < 2 or max(group_rates) == 0:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Cannot compute ratio: fewer than 2 groups or max rate is 0.",
            )

        value = min(group_rates) / max(group_rates)
        status = self.evaluate_status(value, threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "ratio": float(value),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )

"""Calibration by Group metric (BIAS-05)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .base import MIN_SUBGROUP_SIZE, BaseMetric, MetricResult


class CalibrationMetric(BaseMetric):
    """Measures max Expected Calibration Error difference across groups.

    Requires probability scores (``y_prob``).  A value of 0 means groups
    are equally well-calibrated.  Default threshold ≤ 0.05.
    """

    name = "calibration_by_group"
    default_threshold = 0.05
    higher_is_better = False

    @staticmethod
    def _expected_calibration_error(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
    ) -> float:
        """Compute Expected Calibration Error (ECE)."""
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        total = len(y_true)
        if total == 0:
            return 0.0
        for i in range(n_bins):
            if i == 0:
                mask = (y_prob >= bin_edges[i]) & (y_prob <= bin_edges[i + 1])
            else:
                mask = (y_prob > bin_edges[i]) & (y_prob <= bin_edges[i + 1])
            bin_count = mask.sum()
            if bin_count == 0:
                continue
            bin_acc = y_true[mask].mean()
            bin_conf = y_prob[mask].mean()
            ece += (bin_count / total) * abs(bin_acc - bin_conf)
        return float(ece)

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        y_prob: np.ndarray | None = None,
        **kwargs: Any,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        if y_prob is None:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message=(
                    "Calibration requires probability scores (y_prob). "
                    "Model does not support predict_proba."
                ),
            )

        y_true_arr = np.asarray(y_true)
        y_prob_arr = np.asarray(y_prob)
        sf = pd.Series(sensitive_features)

        group_ece: dict[str, float | None] = {}
        for group_name in sf.unique():
            mask = sf == group_name
            group_size = mask.sum()
            if group_size < MIN_SUBGROUP_SIZE:
                group_ece[str(group_name)] = None
                continue
            group_ece[str(group_name)] = self._expected_calibration_error(
                y_true_arr[mask], y_prob_arr[mask]
            )

        valid_eces = [v for v in group_ece.values() if v is not None]
        if len(valid_eces) < 2:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Not enough valid groups for calibration comparison.",
            )

        value = max(valid_eces) - min(valid_eces)
        status = self.evaluate_status(value, threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": group_ece,
                "difference": float(value),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )

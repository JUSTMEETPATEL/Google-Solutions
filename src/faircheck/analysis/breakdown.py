"""Per-group performance breakdown (BIAS-08).

Computes accuracy, precision, recall, F1 for each demographic subgroup
using Fairlearn's MetricFrame.
"""

from __future__ import annotations

import functools

import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


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

"""Intersectional bias detection — analyse pairwise attribute combinations.

EU AI Act Article 10 requires examining intersectional effects.
A model may pass on gender and race individually, but fail for
'Black + Female' as a combined subgroup.
"""

from __future__ import annotations

import logging
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

from faircheck.analysis.breakdown import compute_performance_breakdown

logger = logging.getLogger(__name__)

MIN_INTERSECT_SIZE = 15  # Minimum subgroup size to report


def compute_intersectional_analysis(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: dict[str, pd.Series],
    metrics: list[Any] | None = None,
    thresholds: dict[str, float] | None = None,
    warning_factor: float = 0.8,
) -> dict[str, Any]:
    """Run fairness analysis on every pairwise combination of protected attrs.

    Parameters
    ----------
    y_true, y_pred : array-like
        Ground truth and predicted labels.
    sensitive_features : dict[str, Series]
        Mapping of attribute name → column values.
    metrics : list[BaseMetric], optional
        Metric instances to compute. Uses default group metrics if None.
    thresholds : dict, optional
        Override thresholds keyed by metric name.
    warning_factor : float
        Warning factor for status evaluation.

    Returns
    -------
    dict with:
        - ``intersections``: list of intersection results
        - ``most_disadvantaged``: the group with lowest positive prediction rate
    """
    if len(sensitive_features) < 2:
        return {"intersections": [], "most_disadvantaged": None}

    if metrics is None:
        from faircheck.analysis.engine import _GROUP_METRICS
        metrics = _GROUP_METRICS

    thresholds = thresholds or {}

    attr_names = list(sensitive_features.keys())
    all_intersections: list[dict[str, Any]] = []
    lowest_rate_group = None
    lowest_rate = 1.0

    for attr_a, attr_b in combinations(attr_names, 2):
        vals_a = sensitive_features[attr_a].astype(str)
        vals_b = sensitive_features[attr_b].astype(str)
        combined = vals_a + " × " + vals_b
        combined_name = f"{attr_a} × {attr_b}"

        # Filter groups below minimum size
        group_counts = combined.value_counts()
        valid_groups = group_counts[group_counts >= MIN_INTERSECT_SIZE].index
        if len(valid_groups) < 2:
            logger.info(
                "Skipping intersection %s: insufficient subgroup sizes",
                combined_name,
            )
            continue

        mask = combined.isin(valid_groups)
        filtered_combined = combined[mask]
        filtered_y_true = y_true[mask]
        filtered_y_pred = y_pred[mask]

        # Compute metrics on combined attribute
        metrics_out: dict[str, Any] = {}
        for metric in metrics:
            threshold = thresholds.get(metric.name, metric.default_threshold)
            try:
                result = metric.compute(
                    y_true=filtered_y_true,
                    y_pred=filtered_y_pred,
                    sensitive_features=filtered_combined,
                    threshold=threshold,
                    warning_factor=warning_factor,
                )
                metrics_out[metric.name] = {
                    "name": result.name,
                    "value": result.value,
                    "threshold": result.threshold,
                    "status": result.status,
                    "details": result.details,
                    "warning_message": result.warning_message,
                }
            except Exception as e:
                logger.warning(
                    "Metric %s failed for intersection %s: %s",
                    metric.name, combined_name, e,
                )

        # Compute per-group breakdown for this intersection
        try:
            breakdown = compute_performance_breakdown(
                y_true=filtered_y_true,
                y_pred=filtered_y_pred,
                sensitive_features=filtered_combined,
            )
        except Exception:
            breakdown = {}

        # Compute per-group positive prediction rates
        group_rates: dict[str, dict[str, Any]] = {}
        for group_val in valid_groups:
            g_mask = filtered_combined == group_val
            g_count = int(g_mask.sum())
            g_pred_rate = float(filtered_y_pred[g_mask].mean()) if g_count > 0 else 0.0
            g_true_rate = float(filtered_y_true[g_mask].mean()) if g_count > 0 else 0.0
            group_rates[group_val] = {
                "count": g_count,
                "predicted_positive_rate": round(g_pred_rate, 4),
                "actual_positive_rate": round(g_true_rate, 4),
            }
            if g_pred_rate < lowest_rate:
                lowest_rate = g_pred_rate
                lowest_rate_group = {
                    "group": group_val,
                    "intersection": combined_name,
                    "predicted_positive_rate": round(g_pred_rate, 4),
                    "count": g_count,
                }

        all_intersections.append({
            "intersection": combined_name,
            "metrics": metrics_out,
            "performance_breakdown": breakdown,
            "group_rates": group_rates,
            "n_valid_groups": len(valid_groups),
        })

    return {
        "intersections": all_intersections,
        "most_disadvantaged": lowest_rate_group,
    }

"""Bootstrap confidence intervals for fairness metrics.

Provides statistical significance testing so FairCheck doesn't flag
a metric as 'fail' when the difference is within noise range for
small subgroups.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def bootstrap_confidence_interval(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.Series,
    metric_fn: Any,
    n_bootstrap: int = 500,
    confidence_level: float = 0.95,
    threshold: float | None = None,
    warning_factor: float = 0.8,
    **metric_kwargs: Any,
) -> dict[str, Any]:
    """Compute bootstrap CI for a fairness metric.

    Parameters
    ----------
    y_true, y_pred : array-like
        Ground truth and predictions.
    sensitive_features : Series
        Protected attribute values.
    metric_fn : BaseMetric
        A metric instance with a ``compute()`` method.
    n_bootstrap : int
        Number of bootstrap iterations (default 500).
    confidence_level : float
        CI level (default 0.95 for 95% CI).
    threshold : float, optional
        Metric threshold for status evaluation.
    warning_factor : float
        Warning factor for status evaluation.

    Returns
    -------
    dict with keys:
        - ``point_estimate``: the metric value on full data
        - ``ci_lower``, ``ci_upper``: confidence interval bounds
        - ``is_significant``: True if CI excludes threshold
        - ``n_bootstrap``: number of iterations used
        - ``confidence_level``: CI level used
    """
    n = len(y_true)
    if n < 30:
        # Too small for reliable bootstrapping
        return {
            "point_estimate": None,
            "ci_lower": None,
            "ci_upper": None,
            "is_significant": False,
            "n_bootstrap": 0,
            "confidence_level": confidence_level,
            "note": "Sample too small for bootstrap (n < 30)",
        }

    threshold = threshold or metric_fn.default_threshold

    # Compute point estimate
    try:
        result = metric_fn.compute(
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
            threshold=threshold,
            warning_factor=warning_factor,
            **metric_kwargs,
        )
        point_estimate = result.value
    except Exception as e:
        logger.warning("Point estimate failed for %s: %s", metric_fn.name, e)
        return {
            "point_estimate": None,
            "ci_lower": None,
            "ci_upper": None,
            "is_significant": False,
            "n_bootstrap": 0,
            "confidence_level": confidence_level,
            "note": f"Computation failed: {e}",
        }

    if point_estimate is None:
        return {
            "point_estimate": None,
            "ci_lower": None,
            "ci_upper": None,
            "is_significant": False,
            "n_bootstrap": 0,
            "confidence_level": confidence_level,
        }

    # Bootstrap
    rng = np.random.default_rng(42)
    boot_values: list[float] = []

    for _ in range(n_bootstrap):
        indices = rng.integers(0, n, size=n)
        boot_y_true = y_true[indices]
        boot_y_pred = y_pred[indices]
        boot_sf = sensitive_features.iloc[indices].reset_index(drop=True)

        # Ensure at least 2 unique groups in the bootstrap sample
        if boot_sf.nunique() < 2:
            continue

        try:
            boot_result = metric_fn.compute(
                y_true=boot_y_true,
                y_pred=boot_y_pred,
                sensitive_features=boot_sf,
                threshold=threshold,
                warning_factor=warning_factor,
                **metric_kwargs,
            )
            if boot_result.value is not None:
                boot_values.append(boot_result.value)
        except Exception:
            continue

    if len(boot_values) < 50:
        return {
            "point_estimate": round(point_estimate, 6),
            "ci_lower": None,
            "ci_upper": None,
            "is_significant": False,
            "n_bootstrap": len(boot_values),
            "confidence_level": confidence_level,
            "note": "Insufficient valid bootstrap samples",
        }

    alpha = 1 - confidence_level
    ci_lower = float(np.percentile(boot_values, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_values, 100 * (1 - alpha / 2)))

    # Determine significance: does the CI exclude the "fair" value?
    # For most metrics (lower is better), "fair" = 0; significant if ci_lower > threshold
    # For higher_is_better metrics (disparate impact), significant if ci_upper < threshold
    if metric_fn.higher_is_better:
        is_significant = ci_upper < threshold
    else:
        is_significant = ci_lower > threshold

    return {
        "point_estimate": round(point_estimate, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "is_significant": is_significant,
        "n_bootstrap": len(boot_values),
        "confidence_level": confidence_level,
    }


def compute_all_confidence_intervals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: dict[str, pd.Series],
    metrics: list[Any] | None = None,
    n_bootstrap: int = 500,
    confidence_level: float = 0.95,
    thresholds: dict[str, float] | None = None,
    warning_factor: float = 0.8,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Compute bootstrap CIs for all metrics across all attributes.

    Returns
    -------
    dict keyed by attribute name, each containing a dict keyed by
    metric name with CI results.
    """
    if metrics is None:
        from faircheck.analysis.engine import _GROUP_METRICS
        metrics = _GROUP_METRICS

    thresholds = thresholds or {}
    results: dict[str, dict[str, dict[str, Any]]] = {}

    for attr_name, attr_values in sensitive_features.items():
        attr_results: dict[str, dict[str, Any]] = {}
        for metric in metrics:
            threshold = thresholds.get(metric.name, metric.default_threshold)
            kwargs: dict[str, Any] = {}
            ci = bootstrap_confidence_interval(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=pd.Series(attr_values),
                metric_fn=metric,
                n_bootstrap=n_bootstrap,
                confidence_level=confidence_level,
                threshold=threshold,
                warning_factor=warning_factor,
                **kwargs,
            )
            attr_results[metric.name] = ci
        results[attr_name] = attr_results

    return results

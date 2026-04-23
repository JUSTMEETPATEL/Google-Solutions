"""Temporal drift monitoring — compare fairness metrics across sessions.

Detects model degradation over time by comparing metric values between
scan sessions, identifying which metrics have worsened and by how much.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def compute_drift(
    baseline_results: dict[str, Any],
    current_results: dict[str, Any],
) -> dict[str, Any]:
    """Compare two analysis result sets and compute metric drift.

    Parameters
    ----------
    baseline_results : dict
        Analysis results from the baseline session (``AnalysisResult.to_dict()``).
    current_results : dict
        Analysis results from the current session.

    Returns
    -------
    dict with keys:
        - ``overall_drift``: 'improved', 'stable', or 'degraded'
        - ``risk_change``: change in overall risk level
        - ``per_attribute``: per-attribute metric drift details
        - ``alerts``: list of metrics that crossed a threshold
        - ``summary``: plain-English drift summary
    """
    baseline_risk = baseline_results.get("overall_risk_level", "unknown")
    current_risk = current_results.get("overall_risk_level", "unknown")

    baseline_attrs = baseline_results.get("results", {})
    current_attrs = current_results.get("results", {})

    per_attribute: dict[str, dict[str, Any]] = {}
    alerts: list[dict[str, str]] = []
    total_improved = 0
    total_degraded = 0
    total_stable = 0

    # Compare each attribute's metrics
    shared_attrs = set(baseline_attrs.keys()) & set(current_attrs.keys())
    new_attrs = set(current_attrs.keys()) - set(baseline_attrs.keys())
    removed_attrs = set(baseline_attrs.keys()) - set(current_attrs.keys())

    for attr_name in shared_attrs:
        baseline_metrics = baseline_attrs[attr_name].get("metrics", {})
        current_metrics = current_attrs[attr_name].get("metrics", {})
        metric_drifts: dict[str, dict[str, Any]] = {}

        for metric_name in set(baseline_metrics.keys()) & set(current_metrics.keys()):
            b_data = baseline_metrics[metric_name]
            c_data = current_metrics[metric_name]
            b_val = b_data.get("value")
            c_val = c_data.get("value")
            b_status = b_data.get("status", "")
            c_status = c_data.get("status", "")

            if b_val is None or c_val is None:
                metric_drifts[metric_name] = {
                    "direction": "unknown",
                    "baseline_value": b_val,
                    "current_value": c_val,
                }
                continue

            delta = c_val - b_val
            threshold = c_data.get("threshold", b_data.get("threshold", 0))

            # Determine direction based on metric type
            # For most metrics (lower = better), positive delta = degraded
            # For disparate impact (higher = better), negative delta = degraded
            is_ratio_metric = "ratio" in metric_name or "impact" in metric_name
            if is_ratio_metric:
                direction = "improved" if delta > 0.005 else ("degraded" if delta < -0.005 else "stable")
            else:
                direction = "improved" if delta < -0.005 else ("degraded" if delta > 0.005 else "stable")

            if direction == "improved":
                total_improved += 1
            elif direction == "degraded":
                total_degraded += 1
            else:
                total_stable += 1

            metric_drifts[metric_name] = {
                "direction": direction,
                "baseline_value": round(b_val, 6),
                "current_value": round(c_val, 6),
                "delta": round(delta, 6),
                "baseline_status": b_status,
                "current_status": c_status,
            }

            # Generate alert if status worsened
            status_order = {"pass": 0, "warning": 1, "fail": 2}
            if status_order.get(c_status, 0) > status_order.get(b_status, 0):
                alerts.append({
                    "attribute": attr_name,
                    "metric": metric_name,
                    "severity": "critical" if c_status == "fail" else "warning",
                    "message": (
                        f"{metric_name} for '{attr_name}' changed from "
                        f"'{b_status}' to '{c_status}' "
                        f"(value: {b_val:.4f} → {c_val:.4f})"
                    ),
                })

        per_attribute[attr_name] = {
            "metrics": metric_drifts,
        }

    # Determine overall drift direction
    if total_degraded > total_improved:
        overall_drift = "degraded"
    elif total_improved > total_degraded:
        overall_drift = "improved"
    else:
        overall_drift = "stable"

    # Risk level change
    risk_order = {"low": 0, "medium": 1, "high": 2, "unknown": -1}
    risk_delta = risk_order.get(current_risk, -1) - risk_order.get(baseline_risk, -1)
    if risk_delta > 0:
        risk_change = "worsened"
    elif risk_delta < 0:
        risk_change = "improved"
    else:
        risk_change = "unchanged"

    # Generate summary
    summary = _generate_drift_summary(
        overall_drift, risk_change, baseline_risk, current_risk,
        total_improved, total_degraded, total_stable, len(alerts),
    )

    return {
        "overall_drift": overall_drift,
        "risk_change": risk_change,
        "baseline_risk_level": baseline_risk,
        "current_risk_level": current_risk,
        "per_attribute": per_attribute,
        "alerts": alerts,
        "summary": summary,
        "stats": {
            "metrics_improved": total_improved,
            "metrics_degraded": total_degraded,
            "metrics_stable": total_stable,
            "new_attributes": list(new_attrs),
            "removed_attributes": list(removed_attrs),
        },
    }


def _generate_drift_summary(
    overall: str, risk_change: str,
    baseline_risk: str, current_risk: str,
    improved: int, degraded: int, stable: int,
    alert_count: int,
) -> str:
    """Generate a plain-English drift summary."""
    parts = []

    if overall == "degraded":
        parts.append(
            f"⚠️ Model fairness has DEGRADED since the last audit. "
            f"{degraded} metric(s) worsened while {improved} improved."
        )
    elif overall == "improved":
        parts.append(
            f"✅ Model fairness has IMPROVED since the last audit. "
            f"{improved} metric(s) improved while {degraded} worsened."
        )
    else:
        parts.append(
            f"Model fairness is STABLE since the last audit. "
            f"{stable} metric(s) unchanged."
        )

    if risk_change == "worsened":
        parts.append(
            f"Risk level increased from {baseline_risk.upper()} to {current_risk.upper()}."
        )
    elif risk_change == "improved":
        parts.append(
            f"Risk level decreased from {baseline_risk.upper()} to {current_risk.upper()}."
        )

    if alert_count > 0:
        parts.append(
            f"{alert_count} metric(s) crossed a threshold boundary — review required."
        )

    return " ".join(parts)

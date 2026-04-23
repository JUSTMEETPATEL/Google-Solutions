"""Plain-English metric explanations for compliance officers.

Translates raw metric names and values into human-readable explanations
that a non-technical compliance officer can understand and include in
regulatory reports.
"""

from __future__ import annotations

from typing import Any


# Maps metric name → explanation template generator
_EXPLANATIONS: dict[str, Any] = {}


def _fmt_pct(value: float) -> str:
    """Format a decimal as a percentage string."""
    return f"{abs(value) * 100:.1f}%"


def _fmt_ratio(value: float) -> str:
    """Format a ratio to 2 decimal places."""
    return f"{value:.2f}"


def generate_explanation(
    metric_name: str,
    metric_value: float | None,
    threshold: float,
    status: str,
    attr_name: str,
    details: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Generate a plain-English explanation for a metric result.

    Parameters
    ----------
    metric_name : str
        Internal metric name (e.g., 'demographic_parity_difference').
    metric_value : float or None
        The computed metric value.
    threshold : float
        The threshold for pass/fail.
    status : str
        'pass', 'warning', or 'fail'.
    attr_name : str
        Name of the protected attribute (e.g., 'gender').
    details : dict, optional
        Additional metric details (e.g., per-group rates).

    Returns
    -------
    dict with keys:
        - ``summary``: one-sentence plain-English verdict
        - ``detail``: multi-sentence explanation of what the metric measures
        - ``recommendation``: actionable next step
        - ``severity``: 'pass', 'warning', 'fail'
    """
    if metric_value is None:
        return {
            "summary": f"The {_friendly_name(metric_name)} metric could not be computed.",
            "detail": "This may indicate insufficient data or an incompatible model configuration.",
            "recommendation": "Ensure the dataset has sufficient samples across all demographic groups.",
            "severity": "skipped",
        }

    fn = _EXPLANATIONS.get(metric_name, _generic_explanation)
    return fn(metric_name, metric_value, threshold, status, attr_name, details or {})


def generate_all_explanations(
    results: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, str]]]:
    """Generate explanations for all metrics across all attributes.

    Parameters
    ----------
    results : dict
        The ``results`` dict from AnalysisResult, keyed by attribute name.

    Returns
    -------
    dict keyed by attribute name, each containing a dict keyed by metric name.
    """
    output: dict[str, dict[str, dict[str, str]]] = {}
    for attr_name, attr_data in results.items():
        attr_explanations: dict[str, dict[str, str]] = {}
        for metric_name, metric_data in attr_data.get("metrics", {}).items():
            attr_explanations[metric_name] = generate_explanation(
                metric_name=metric_name,
                metric_value=metric_data.get("value"),
                threshold=metric_data.get("threshold", 0),
                status=metric_data.get("status", "skipped"),
                attr_name=attr_name,
                details=metric_data.get("details"),
            )
        output[attr_name] = attr_explanations
    return output


def _friendly_name(metric_name: str) -> str:
    """Convert internal name to friendly display name."""
    names = {
        "demographic_parity_difference": "Demographic Parity",
        "equalized_odds_difference": "Equalized Odds",
        "disparate_impact_ratio": "Disparate Impact (4/5ths Rule)",
        "predictive_parity": "Predictive Parity",
        "calibration_by_group": "Calibration by Group",
        "individual_fairness": "Individual Fairness",
    }
    return names.get(metric_name, metric_name.replace("_", " ").title())


def _status_emoji(status: str) -> str:
    """Return a status indicator for text reports."""
    return {"pass": "✅", "warning": "⚠️", "fail": "❌"}.get(status, "❓")


# ─── Per-Metric Explanation Functions ────────────────────────


def _demographic_parity(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    direction = "higher" if value > 0 else "lower"
    groups = details.get("group_rates", {})
    group_info = ""
    if groups:
        sorted_groups = sorted(groups.items(), key=lambda x: x[1])
        if len(sorted_groups) >= 2:
            lowest_name, lowest_rate = sorted_groups[0]
            highest_name, highest_rate = sorted_groups[-1]
            group_info = (
                f" Specifically, '{highest_name}' has a positive outcome rate of "
                f"{_fmt_pct(highest_rate)}, while '{lowest_name}' has only {_fmt_pct(lowest_rate)}."
            )

    if status == "pass":
        summary = (
            f"{_status_emoji(status)} The model treats all {attr} groups approximately equally "
            f"in terms of selection rates (difference: {_fmt_pct(value)}, threshold: {_fmt_pct(threshold)})."
        )
        recommendation = "No immediate action required. Continue monitoring."
    elif status == "warning":
        summary = (
            f"{_status_emoji(status)} The model shows a slight disparity of {_fmt_pct(value)} "
            f"across {attr} groups, approaching the {_fmt_pct(threshold)} threshold.{group_info}"
        )
        recommendation = (
            "Consider applying pre-processing mitigation (e.g., reweighing) to reduce "
            "the gap before it becomes a compliance issue."
        )
    else:
        summary = (
            f"{_status_emoji(status)} The model shows a significant selection rate disparity of "
            f"{_fmt_pct(value)} across {attr} groups, exceeding the {_fmt_pct(threshold)} "
            f"acceptable threshold.{group_info}"
        )
        recommendation = (
            "Immediate action required. Apply bias mitigation (reweighing or equalized odds "
            "post-processing) and re-audit. This disparity may violate EEOC guidelines and "
            "EU AI Act Article 10."
        )

    return {
        "summary": summary,
        "detail": (
            "Demographic Parity measures whether the positive outcome rate is equal "
            "across all demographic groups defined by the protected attribute. A difference "
            "of 0 indicates perfect parity; values further from 0 indicate greater disparity."
        ),
        "recommendation": recommendation,
        "severity": status,
    }


def _equalized_odds(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    if status == "pass":
        summary = (
            f"{_status_emoji(status)} The model's error rates (true positive and false positive rates) "
            f"are consistent across {attr} groups (difference: {_fmt_pct(value)})."
        )
        recommendation = "No action needed. Error rates are balanced."
    elif status == "warning":
        summary = (
            f"{_status_emoji(status)} The model shows slightly unequal error rates across {attr} groups "
            f"(difference: {_fmt_pct(value)}, threshold: {_fmt_pct(threshold)})."
        )
        recommendation = (
            "Monitor closely. Consider equalized odds post-processing if the gap increases."
        )
    else:
        summary = (
            f"{_status_emoji(status)} The model has significantly different error rates across {attr} "
            f"groups (difference: {_fmt_pct(value)}). Some groups may experience more false "
            f"negatives or false positives than others."
        )
        recommendation = (
            "Apply equalized odds or calibrated equalized odds post-processing to balance "
            "error rates. This disparity may violate EU AI Act Article 9 requirements."
        )

    return {
        "summary": summary,
        "detail": (
            "Equalized Odds measures whether a model makes errors at the same rate across "
            "all demographic groups. It compares both the True Positive Rate (correctly "
            "identified positives) and False Positive Rate (incorrectly flagged negatives) "
            "across groups."
        ),
        "recommendation": recommendation,
        "severity": status,
    }


def _disparate_impact(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    if status == "pass":
        summary = (
            f"{_status_emoji(status)} The model satisfies the 4/5ths rule for {attr} "
            f"(ratio: {_fmt_ratio(value)}, minimum: {_fmt_ratio(threshold)})."
        )
        recommendation = "Compliant with EEOC 4/5ths rule. No action needed."
    elif status == "warning":
        summary = (
            f"{_status_emoji(status)} The model's disparate impact ratio for {attr} is "
            f"{_fmt_ratio(value)}, close to the {_fmt_ratio(threshold)} minimum required "
            f"by the 4/5ths rule."
        )
        recommendation = (
            "The selection rate ratio is borderline. Consider proactive mitigation."
        )
    else:
        summary = (
            f"{_status_emoji(status)} The model FAILS the 4/5ths rule for {attr} — the least "
            f"favored group's selection rate is only {_fmt_ratio(value)} times that of the most "
            f"favored group (minimum required: {_fmt_ratio(threshold)})."
        )
        recommendation = (
            "This is a regulatory compliance failure under EEOC guidelines. Apply disparate "
            "impact remover or reweighing, then re-audit. Document the remediation."
        )

    return {
        "summary": summary,
        "detail": (
            "Disparate Impact Ratio (the '4/5ths Rule') compares the positive outcome rate "
            "of the least favored group to the most favored group. Under EEOC guidelines, "
            "this ratio must be at least 0.80 (80%). Values below this indicate illegal "
            "adverse impact in employment contexts."
        ),
        "recommendation": recommendation,
        "severity": status,
    }


def _predictive_parity(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    if status == "pass":
        summary = (
            f"{_status_emoji(status)} When the model predicts a positive outcome, it is "
            f"equally accurate across all {attr} groups (difference: {_fmt_pct(value)})."
        )
        recommendation = "Predictive accuracy is balanced. No action needed."
    else:
        summary = (
            f"{_status_emoji(status)} The model's positive predictions are {_fmt_pct(value)} "
            f"{'less' if value > 0 else 'more'} accurate for some {attr} groups than others."
        )
        recommendation = (
            "Consider calibrated equalized odds post-processing to balance predictive accuracy."
        )

    return {
        "summary": summary,
        "detail": (
            "Predictive Parity measures whether the Positive Predictive Value (precision) "
            "is equal across groups. When this metric fails, it means a positive prediction "
            "is more likely to be correct for some groups than others."
        ),
        "recommendation": recommendation,
        "severity": status,
    }


def _calibration(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    if status == "pass":
        summary = (
            f"{_status_emoji(status)} The model's predicted probabilities are well-calibrated "
            f"across all {attr} groups (calibration error: {_fmt_pct(value)})."
        )
        recommendation = "Calibration is consistent. No action needed."
    else:
        summary = (
            f"{_status_emoji(status)} The model's predicted probabilities differ in reliability "
            f"across {attr} groups (calibration error: {_fmt_pct(value)}, threshold: {_fmt_pct(threshold)}). "
            f"A predicted 70% probability may mean 70% for one group but only 50% for another."
        )
        recommendation = (
            "Apply calibration-aware post-processing (Platt scaling per group) or "
            "calibrated equalized odds to align probabilities. Critical for healthcare "
            "and lending decisions."
        )

    return {
        "summary": summary,
        "detail": (
            "Calibration by Group measures whether predicted probabilities match actual "
            "outcomes equally across demographics. In healthcare, poor calibration means "
            "the same risk score may represent different actual risks for different patient "
            "populations."
        ),
        "recommendation": recommendation,
        "severity": status,
    }


def _generic_explanation(
    name: str, value: float, threshold: float, status: str,
    attr: str, details: dict,
) -> dict[str, str]:
    friendly = _friendly_name(name)
    if status == "pass":
        summary = (
            f"{_status_emoji(status)} The {friendly} metric is within acceptable bounds "
            f"for {attr} (value: {value:.4f}, threshold: {threshold})."
        )
        recommendation = "No action required."
    elif status == "warning":
        summary = (
            f"{_status_emoji(status)} The {friendly} metric is approaching the threshold "
            f"for {attr} (value: {value:.4f}, threshold: {threshold})."
        )
        recommendation = "Monitor and consider proactive mitigation."
    else:
        summary = (
            f"{_status_emoji(status)} The {friendly} metric exceeds the acceptable threshold "
            f"for {attr} (value: {value:.4f}, threshold: {threshold})."
        )
        recommendation = "Apply appropriate bias mitigation and re-audit."

    return {
        "summary": summary,
        "detail": f"The {friendly} metric evaluates fairness across demographic groups.",
        "recommendation": recommendation,
        "severity": status,
    }


# Register all explanations
_EXPLANATIONS["demographic_parity_difference"] = _demographic_parity
_EXPLANATIONS["equalized_odds_difference"] = _equalized_odds
_EXPLANATIONS["disparate_impact_ratio"] = _disparate_impact
_EXPLANATIONS["predictive_parity"] = _predictive_parity
_EXPLANATIONS["calibration_by_group"] = _calibration

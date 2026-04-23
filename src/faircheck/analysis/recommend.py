"""Auto-recommend mitigation algorithms based on analysis results.

Inspects the bias analysis to determine which mitigation strategies are
most likely to be effective for the specific bias patterns detected.
"""

from __future__ import annotations

from typing import Any


def recommend_mitigation(
    analysis_results: dict[str, Any],
    has_training_data: bool = True,
) -> list[dict[str, Any]]:
    """Rank mitigation algorithms by likely effectiveness.

    Parameters
    ----------
    analysis_results : dict
        From ``AnalysisResult.to_dict()``.
    has_training_data : bool
        Whether original training data is available (enables pre-processing).

    Returns
    -------
    list of dicts, each containing:
        - ``algorithm``: algorithm name
        - ``category``: pre/in/post-processing
        - ``confidence``: estimated effectiveness (high/medium/low)
        - ``rationale``: why this algorithm is recommended
        - ``addresses``: list of metric names it targets
        - ``priority``: 1 = best recommendation
    """
    results = analysis_results.get("results", {})
    if not results:
        return []

    # Aggregate failing/warning metrics across all attributes
    failing_metrics: dict[str, list[str]] = {}  # metric_name → [attributes]
    warning_metrics: dict[str, list[str]] = {}
    metric_values: dict[str, float] = {}

    for attr_name, attr_data in results.items():
        for metric_name, metric_data in attr_data.get("metrics", {}).items():
            status = metric_data.get("status", "")
            value = metric_data.get("value")
            if status == "fail":
                failing_metrics.setdefault(metric_name, []).append(attr_name)
                if value is not None:
                    metric_values[metric_name] = value
            elif status == "warning":
                warning_metrics.setdefault(metric_name, []).append(attr_name)
                if value is not None:
                    metric_values[metric_name] = value

    all_problematic = set(failing_metrics.keys()) | set(warning_metrics.keys())
    if not all_problematic:
        return [{
            "algorithm": "none",
            "category": "none",
            "confidence": "high",
            "rationale": "All fairness metrics pass. No mitigation is needed at this time.",
            "addresses": [],
            "priority": 1,
        }]

    recommendations: list[dict[str, Any]] = []

    # ── Decision logic ────────────────────────────────────────

    # 1. Demographic Parity / Disparate Impact → Reweighing (pre-processing)
    dp_failing = "demographic_parity_difference" in failing_metrics
    di_failing = "disparate_impact_ratio" in failing_metrics
    if (dp_failing or di_failing) and has_training_data:
        attrs = list(set(
            failing_metrics.get("demographic_parity_difference", []) +
            failing_metrics.get("disparate_impact_ratio", [])
        ))
        recommendations.append({
            "algorithm": "reweighing",
            "category": "pre-processing",
            "confidence": "high",
            "rationale": (
                "Selection rate disparities detected across groups. Reweighing adjusts "
                "training sample weights to equalize selection rates without modifying "
                "the data itself. This is the least invasive and most commonly recommended "
                "approach for demographic parity and disparate impact issues."
            ),
            "addresses": [m for m in ["demographic_parity_difference", "disparate_impact_ratio"]
                         if m in all_problematic],
            "target_attributes": attrs,
            "priority": 0,  # Will be set later
        })

    # 2. Equalized Odds → Equalized Odds Post-processing
    if "equalized_odds_difference" in all_problematic:
        attrs = (failing_metrics.get("equalized_odds_difference", []) +
                 warning_metrics.get("equalized_odds_difference", []))
        recommendations.append({
            "algorithm": "equalized_odds",
            "category": "post-processing",
            "confidence": "high" if "equalized_odds_difference" in failing_metrics else "medium",
            "rationale": (
                "Unequal error rates detected across groups. Equalized Odds post-processing "
                "adjusts the decision threshold per group to balance True Positive and "
                "False Positive rates. Works with any model without retraining."
            ),
            "addresses": ["equalized_odds_difference"],
            "target_attributes": list(set(attrs)),
            "priority": 0,
        })

    # 3. Calibration issues → Calibrated Equalized Odds
    if "calibration_by_group" in all_problematic:
        attrs = (failing_metrics.get("calibration_by_group", []) +
                 warning_metrics.get("calibration_by_group", []))
        recommendations.append({
            "algorithm": "calibrated_equalized_odds",
            "category": "post-processing",
            "confidence": "high" if "calibration_by_group" in failing_metrics else "medium",
            "rationale": (
                "Predicted probabilities are inconsistent across groups. Calibrated "
                "Equalized Odds adjusts predictions while preserving calibration quality. "
                "Particularly important for healthcare and lending applications."
            ),
            "addresses": ["calibration_by_group", "equalized_odds_difference"],
            "target_attributes": list(set(attrs)),
            "priority": 0,
        })

    # 4. Multiple metric failures with training data → Disparate Impact Remover
    if len(failing_metrics) >= 2 and has_training_data:
        recommendations.append({
            "algorithm": "disparate_impact_remover",
            "category": "pre-processing",
            "confidence": "medium",
            "rationale": (
                "Multiple fairness metrics are failing. Disparate Impact Remover "
                "transforms features to remove their correlation with protected "
                "attributes. More aggressive than reweighing but addresses "
                "systemic feature-level bias."
            ),
            "addresses": list(failing_metrics.keys()),
            "target_attributes": list(set(
                attr for attrs in failing_metrics.values() for attr in attrs
            )),
            "priority": 0,
        })

    # 5. Predictive parity → Reject Option Classification
    if "predictive_parity" in all_problematic:
        attrs = (failing_metrics.get("predictive_parity", []) +
                 warning_metrics.get("predictive_parity", []))
        recommendations.append({
            "algorithm": "reject_option_classification",
            "category": "post-processing",
            "confidence": "medium",
            "rationale": (
                "Predictions near the decision boundary show group-dependent accuracy. "
                "Reject Option Classification reassigns predictions in the uncertain "
                "region to favor disadvantaged groups."
            ),
            "addresses": ["predictive_parity", "demographic_parity_difference"],
            "target_attributes": list(set(attrs)),
            "priority": 0,
        })

    # 6. Severe multi-failure → Adversarial Debiasing (if training data available)
    if len(failing_metrics) >= 3 and has_training_data:
        recommendations.append({
            "algorithm": "adversarial_debiasing",
            "category": "in-processing",
            "confidence": "low",
            "rationale": (
                "Severe bias detected across multiple metrics. Adversarial Debiasing "
                "trains a competing network to prevent the model from using protected "
                "attribute information. Most aggressive option — may reduce accuracy."
            ),
            "addresses": list(all_problematic),
            "target_attributes": list(set(
                attr for attrs in failing_metrics.values() for attr in attrs
            )),
            "priority": 0,
        })

    # Set priorities (1 = best)
    # Prioritize: high confidence post-processing > pre-processing > in-processing
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    category_order = {"post-processing": 0, "pre-processing": 1, "in-processing": 2}
    recommendations.sort(
        key=lambda r: (
            confidence_order.get(r["confidence"], 3),
            category_order.get(r["category"], 3),
        )
    )
    for i, rec in enumerate(recommendations):
        rec["priority"] = i + 1

    return recommendations

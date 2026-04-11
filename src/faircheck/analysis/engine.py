"""BiasAnalyzer — orchestrates all fairness metrics for a scan.

Usage::

    from faircheck.analysis.engine import BiasAnalyzer
    from faircheck.config import load_config

    analyzer = BiasAnalyzer(config=load_config())
    results = analyzer.analyze(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features={"gender": gender_col, "race": race_col},
        y_prob=y_prob,          # optional
        feature_matrix=X_test,  # optional, for individual fairness
        domain="hiring",        # optional
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from faircheck.analysis.breakdown import compute_performance_breakdown
from faircheck.analysis.domains import get_domain_guidance
from faircheck.analysis.metrics import (
    CalibrationMetric,
    DemographicParityMetric,
    DisparateImpactMetric,
    EqualizedOddsMetric,
    IndividualFairnessMetric,
    MetricResult,
    PredictiveParityMetric,
)

logger = logging.getLogger(__name__)

# All group-level metrics (run per protected attribute)
_GROUP_METRICS = [
    DemographicParityMetric(),
    EqualizedOddsMetric(),
    DisparateImpactMetric(),
    PredictiveParityMetric(),
    CalibrationMetric(),
]

# Global metric (not per-attribute)
_INDIVIDUAL_METRIC = IndividualFairnessMetric()


@dataclass
class AnalysisResult:
    """Full bias analysis output — serializable to JSON."""

    protected_attributes: list[str]
    results: dict[str, dict[str, Any]]
    individual_fairness: dict[str, Any] | None
    domain_guidance: dict[str, Any] | None
    overall_risk_level: str
    scan_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (JSON-compatible)."""
        return {
            "protected_attributes": self.protected_attributes,
            "results": self.results,
            "individual_fairness": self.individual_fairness,
            "domain_guidance": self.domain_guidance,
            "overall_risk_level": self.overall_risk_level,
            "scan_metadata": self.scan_metadata,
        }


class BiasAnalyzer:
    """Orchestrates all fairness metrics across protected attributes."""

    def __init__(self, config: dict | None = None) -> None:
        from faircheck.config import DEFAULT_CONFIG

        self.config = config or DEFAULT_CONFIG

    def analyze(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: dict[str, pd.Series],
        y_prob: np.ndarray | None = None,
        feature_matrix: np.ndarray | pd.DataFrame | None = None,
        domain: str | None = None,
    ) -> AnalysisResult:
        """Run all metrics for each protected attribute.

        Parameters
        ----------
        y_true : array-like
            Ground truth labels.
        y_pred : array-like
            Model predictions.
        sensitive_features : dict[str, Series]
            Mapping of attribute name → column values.
        y_prob : array-like, optional
            Predicted probabilities (for calibration + individual fairness).
        feature_matrix : array-like, optional
            Non-protected features for individual fairness.
        domain : str, optional
            Domain for guidance (``"hiring"``, ``"lending"``, ``"healthcare"``).

        Returns
        -------
        AnalysisResult
            Complete analysis with nested results per attribute.
        """
        thresholds = self.config.get("metrics", {}).get("default_thresholds", {})
        warning_factor = self.config.get("metrics", {}).get("warning_factor", 0.8)
        if_config = self.config.get("individual_fairness", {})

        attr_names = list(sensitive_features.keys())
        per_attr_results: dict[str, dict[str, Any]] = {}

        for attr_name, attr_values in sensitive_features.items():
            attr_values = pd.Series(attr_values)
            metrics_out: dict[str, Any] = {}

            for metric in _GROUP_METRICS:
                threshold = thresholds.get(metric.name, metric.default_threshold)
                kwargs: dict[str, Any] = {}
                if metric.name == "calibration_by_group":
                    kwargs["y_prob"] = y_prob

                result = metric.compute(
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_features=attr_values,
                    threshold=threshold,
                    warning_factor=warning_factor,
                    **kwargs,
                )
                metrics_out[metric.name] = _result_to_dict(result)

            # Per-group performance breakdown (BIAS-08)
            breakdown = compute_performance_breakdown(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=attr_values,
            )

            per_attr_results[attr_name] = {
                "metrics": metrics_out,
                "performance_breakdown": breakdown,
            }

        # Individual fairness (global, not per-attribute)
        if_result_dict = None
        if feature_matrix is not None and y_prob is not None:
            if_threshold = thresholds.get(
                _INDIVIDUAL_METRIC.name, _INDIVIDUAL_METRIC.default_threshold
            )
            if_result = _INDIVIDUAL_METRIC.compute(
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=pd.Series(dtype=object),  # not used
                threshold=if_threshold,
                warning_factor=warning_factor,
                y_prob=y_prob,
                feature_matrix=feature_matrix,
                lipschitz_constant=if_config.get("lipschitz_constant", 1.0),
                sample_size=if_config.get("sample_size", 1000),
            )
            if_result_dict = _result_to_dict(if_result)

        # Domain guidance (BIAS-09)
        guidance = get_domain_guidance(domain)
        guidance_dict = dict(guidance) if guidance else None
        if guidance_dict and domain:
            guidance_dict["domain"] = domain

        # Overall risk level
        risk = self._compute_risk_level(per_attr_results, if_result_dict)

        metrics_computed = len(_GROUP_METRICS) * len(attr_names)
        if if_result_dict:
            metrics_computed += 1

        return AnalysisResult(
            protected_attributes=attr_names,
            results=per_attr_results,
            individual_fairness=if_result_dict,
            domain_guidance=guidance_dict,
            overall_risk_level=risk,
            scan_metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sample_size": len(y_true),
                "metrics_computed": metrics_computed,
            },
        )

    @staticmethod
    def _compute_risk_level(
        per_attr: dict[str, dict[str, Any]],
        individual: dict[str, Any] | None,
    ) -> str:
        """Derive overall risk: high if any fail, medium if any warn, else low."""
        statuses: list[str] = []
        for attr_data in per_attr.values():
            for metric_data in attr_data.get("metrics", {}).values():
                s = metric_data.get("status")
                if s:
                    statuses.append(s)
        if individual:
            s = individual.get("status")
            if s:
                statuses.append(s)

        if any(s == "fail" for s in statuses):
            return "high"
        if any(s == "warning" for s in statuses):
            return "medium"
        return "low"


def _result_to_dict(r: MetricResult) -> dict[str, Any]:
    """Convert a MetricResult to a plain dict."""
    return {
        "name": r.name,
        "value": r.value,
        "threshold": r.threshold,
        "status": r.status,
        "details": r.details,
        "warning_message": r.warning_message,
    }

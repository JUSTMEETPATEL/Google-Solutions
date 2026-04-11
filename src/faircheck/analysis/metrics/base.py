"""Base classes for fairness metrics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

MIN_SUBGROUP_SIZE = 30


@dataclass
class MetricResult:
    """Result container for a single fairness metric computation."""

    name: str
    value: float | None
    threshold: float
    status: str  # "pass" | "warning" | "fail" | "skipped"
    details: dict[str, Any] = field(default_factory=dict)
    warning_message: str | None = None


class BaseMetric(ABC):
    """Abstract base for all fairness metrics.

    Each metric self-evaluates pass/warning/fail status (D-03).
    """

    name: str
    default_threshold: float
    higher_is_better: bool = False  # Most metrics: lower diff = fairer

    @abstractmethod
    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs: Any,
    ) -> MetricResult:
        """Compute the metric and return a result with status."""
        ...

    def evaluate_status(
        self, value: float, threshold: float, warning_factor: float = 0.8
    ) -> str:
        """Evaluate pass/warning/fail against threshold (D-03, D-05).

        For ``higher_is_better=False`` (most metrics):
            pass    if value <= threshold * warning_factor
            warning if value <= threshold
            fail    otherwise

        For ``higher_is_better=True`` (e.g., disparate impact ratio):
            pass    if value >= threshold + (1 - threshold) * (1 - warning_factor)
            warning if value >= threshold
            fail    otherwise
        """
        if self.higher_is_better:
            warning_bound = threshold + (1.0 - threshold) * (1.0 - warning_factor)
            if value >= warning_bound:
                return "pass"
            elif value >= threshold:
                return "warning"
            else:
                return "fail"
        else:
            warning_bound = threshold * warning_factor
            if value <= warning_bound:
                return "pass"
            elif value <= threshold:
                return "warning"
            else:
                return "fail"

    def _check_subgroup_size(
        self, sensitive_features: pd.Series
    ) -> dict[str, str]:
        """Return warnings for subgroups below MIN_SUBGROUP_SIZE."""
        warnings: dict[str, str] = {}
        for group_name, group_size in sensitive_features.value_counts().items():
            if group_size < MIN_SUBGROUP_SIZE:
                warnings[str(group_name)] = (
                    f"Subgroup '{group_name}' has {group_size} samples "
                    f"(min: {MIN_SUBGROUP_SIZE}). Metric may be unreliable."
                )
        return warnings

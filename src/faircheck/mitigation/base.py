"""Base classes for mitigation algorithms."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class MitigationResult:
    """Result of applying a mitigation algorithm."""

    algorithm: str
    category: str  # "pre-processing" | "in-processing" | "post-processing"
    success: bool
    before_metrics: dict[str, Any] = field(default_factory=dict)
    after_metrics: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "category": self.category,
            "success": self.success,
            "before_metrics": self.before_metrics,
            "after_metrics": self.after_metrics,
            "details": self.details,
            "error": self.error,
        }


class BaseMitigation(ABC):
    """Abstract base for all mitigation algorithms.

    All mitigation algorithms enforce train/test separation (MIT-08):
    transformation is applied ONLY to training data.
    """

    name: str
    category: str  # "pre-processing" | "in-processing" | "post-processing"

    @abstractmethod
    def apply(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray | pd.DataFrame,
        y_test: np.ndarray,
        sensitive_feature: str,
        sensitive_train: pd.Series,
        sensitive_test: pd.Series,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Apply the mitigation and return transformed data + predictions.

        Returns dict with keys depending on category:
        - Pre-processing: ``X_train_transformed``, ``y_train_transformed``,
          ``sample_weight`` (optional)
        - Post-processing: ``y_pred_adjusted``
        - In-processing: ``model`` (the debiased estimator)

        Note: ``X_test`` and ``y_test`` are NEVER modified (MIT-08).
        """
        ...

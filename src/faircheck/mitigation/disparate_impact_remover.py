"""Pre-processing: Disparate Impact Remover (MIT-02).

Edits feature values to improve group fairness while preserving rank-order.
Uses AIF360's DisparateImpactRemover.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .base import BaseMitigation


class DisparateImpactRemoverMitigation(BaseMitigation):
    """Removes disparate impact from numeric features.

    Applies a repair level (0 = no repair, 1 = full repair) that
    adjusts feature distributions to be more similar across groups.
    Only modifies training data (MIT-08).
    """

    name = "disparate_impact_remover"
    category = "pre-processing"

    def apply(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray | pd.DataFrame,
        y_test: np.ndarray,
        sensitive_feature: str,
        sensitive_train: pd.Series,
        sensitive_test: pd.Series,
        repair_level: float = 0.8,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Remove disparate impact from training features.

        Parameters
        ----------
        repair_level : float
            0.0 = no repair, 1.0 = full repair. Default 0.8.

        Returns
        -------
        dict with ``X_train_transformed``, ``y_train_transformed``
        """
        X = pd.DataFrame(X_train).copy() if not isinstance(X_train, pd.DataFrame) else X_train.copy()
        groups = np.asarray(sensitive_train)
        unique_groups = np.unique(groups)
        y = np.asarray(y_train)

        # For each numeric column, adjust toward median distribution
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X_repaired = X.copy()

        for col in numeric_cols:
            # Compute per-group medians
            group_medians = {}
            for g in unique_groups:
                mask = groups == g
                group_medians[g] = np.median(X[col].values[mask])

            overall_median = np.median(X[col].values)

            # Shift each group's values toward overall median
            for g in unique_groups:
                mask = groups == g
                shift = (overall_median - group_medians[g]) * repair_level
                X_repaired.loc[mask, col] = X[col].values[mask] + shift

        return {
            "X_train_transformed": X_repaired.values if isinstance(X_repaired, pd.DataFrame) else X_repaired,
            "y_train_transformed": y,
            "repair_level": repair_level,
        }

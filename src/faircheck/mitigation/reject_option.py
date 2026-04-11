"""Post-processing: Reject Option Classification (MIT-06).

Reassigns labels for borderline predictions near the decision boundary
to the favorable outcome for the disadvantaged group.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .base import BaseMitigation


class RejectOptionClassification(BaseMitigation):
    """Reject option-based classification for fair outcomes.

    For predictions with probabilities close to 0.5 (within
    ``margin``), reassigns the prediction to the favorable
    outcome for the disadvantaged group and unfavorable for
    the privileged group.
    """

    name = "reject_option_classification"
    category = "post-processing"

    def apply(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray | pd.DataFrame,
        y_test: np.ndarray,
        sensitive_feature: str,
        sensitive_train: pd.Series,
        sensitive_test: pd.Series,
        y_prob_test: np.ndarray | None = None,
        margin: float = 0.1,
        privileged_group: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Apply reject option classification to test predictions.

        Parameters
        ----------
        y_prob_test : array-like
            Predicted probabilities on test set. Required.
        margin : float
            Width of critical region around 0.5 threshold. Default 0.1.
        privileged_group : str, optional
            Name of the privileged group. If None, auto-detects as group
            with highest selection rate.

        Returns
        -------
        dict with ``y_pred_adjusted``
        """
        if y_prob_test is None:
            raise ValueError(
                "Reject Option Classification requires probability scores "
                "(y_prob_test). Model must support predict_proba."
            )

        probs = np.asarray(y_prob_test)
        y_pred = (probs >= 0.5).astype(int)
        groups = np.asarray(sensitive_test)
        unique_groups = np.unique(groups)

        # Auto-detect privileged group
        if privileged_group is None:
            group_rates = {}
            for g in unique_groups:
                mask = groups == g
                group_rates[g] = y_pred[mask].mean()
            privileged_group = max(group_rates, key=group_rates.get)

        # Critical region: predictions near the decision boundary
        lower = 0.5 - margin
        upper = 0.5 + margin
        in_critical = (probs >= lower) & (probs <= upper)

        adjusted = y_pred.copy()

        for i in range(len(adjusted)):
            if not in_critical[i]:
                continue
            if groups[i] == privileged_group:
                # Flip to unfavorable in critical region
                adjusted[i] = 0
            else:
                # Flip to favorable in critical region
                adjusted[i] = 1

        return {
            "y_pred_adjusted": adjusted,
            "critical_region": {"lower": lower, "upper": upper},
            "privileged_group": str(privileged_group),
            "samples_adjusted": int(in_critical.sum()),
        }

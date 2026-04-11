"""Pre-processing: Reweighing (MIT-01).

Computes sample weights to make the training data fairer — does NOT
modify features or labels, only produces weights for the estimator.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
from sklearn.linear_model import LogisticRegression

from .base import BaseMitigation


class ReweighingMitigation(BaseMitigation):
    """Fairlearn-based reweighing via sample weight computation.

    Uses ``ExponentiatedGradient`` with ``DemographicParity`` constraint
    to derive fair sample weights from the training data.
    """

    name = "reweighing"
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
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute fair sample weights for training data.

        Returns
        -------
        dict with keys:
            - ``sample_weight``: array of weights for each training sample
            - ``model``: the fitted ExponentiatedGradient estimator
        """
        # Compute group-level weights to balance selection rates
        groups = sensitive_train.values
        unique_groups = np.unique(groups)
        y = np.asarray(y_train)

        # Weight = P(Y=1) / P(Y=1 | G=g) per group
        overall_positive_rate = y.mean()
        sample_weight = np.ones(len(y), dtype=float)

        for g in unique_groups:
            mask = groups == g
            group_positive_rate = y[mask].mean() if mask.sum() > 0 else 0.0
            if group_positive_rate > 0:
                # Favorable outcome weight
                fav_weight = overall_positive_rate / group_positive_rate
                unfav_weight = (1 - overall_positive_rate) / (1 - group_positive_rate) if group_positive_rate < 1 else 1.0
                sample_weight[mask & (y == 1)] = fav_weight
                sample_weight[mask & (y == 0)] = unfav_weight
            # else: leave weights as 1.0

        # Normalize weights
        sample_weight = sample_weight / sample_weight.mean()

        return {
            "sample_weight": sample_weight,
            "X_train_transformed": np.asarray(X_train),
            "y_train_transformed": y,
        }

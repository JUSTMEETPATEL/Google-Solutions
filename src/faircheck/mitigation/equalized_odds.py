"""Post-processing: Equalized Odds Post-processing (MIT-04).

Adjusts predictions to satisfy equalized odds constraint using
Fairlearn's ThresholdOptimizer.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.linear_model import LogisticRegression

from .base import BaseMitigation


class EqualizedOddsPostProcessing(BaseMitigation):
    """Post-processing to achieve equalized odds.

    Uses Fairlearn's ``ThresholdOptimizer`` with ``equalized_odds``
    constraint to find group-specific thresholds that equalize
    TPR and FPR across groups.
    """

    name = "equalized_odds_postprocessing"
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
        estimator: Any = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Adjust test predictions to satisfy equalized odds.

        Parameters
        ----------
        estimator : estimator, optional
            Already-fitted sklearn estimator. If None, fits LogisticRegression.

        Returns
        -------
        dict with ``y_pred_adjusted`` (adjusted test predictions)
        """
        if estimator is None:
            estimator = LogisticRegression(max_iter=1000, solver="lbfgs")
            estimator.fit(np.asarray(X_train), np.asarray(y_train))

        postprocessor = ThresholdOptimizer(
            estimator=estimator,
            constraints="equalized_odds",
            prefit=True,
        )

        postprocessor.fit(
            np.asarray(X_train),
            np.asarray(y_train),
            sensitive_features=np.asarray(sensitive_train),
        )

        y_pred_adjusted = postprocessor.predict(
            np.asarray(X_test),
            sensitive_features=np.asarray(sensitive_test),
            random_state=42,
        )

        return {
            "y_pred_adjusted": np.asarray(y_pred_adjusted),
            "postprocessor": postprocessor,
        }

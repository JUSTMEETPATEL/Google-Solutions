"""Post-processing: Calibrated Equalized Odds (MIT-05).

Adjusts predictions to satisfy equalized odds while preserving
calibration as much as possible.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.linear_model import LogisticRegression

from .base import BaseMitigation


class CalibratedEqualizedOdds(BaseMitigation):
    """Post-processing for calibrated equalized odds.

    Similar to ``EqualizedOddsPostProcessing`` but uses
    ``ThresholdOptimizer`` with ``demographic_parity`` constraint
    which tends to preserve calibration better than strict equalized odds.
    """

    name = "calibrated_equalized_odds"
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
        """Adjust predictions for calibrated equalized odds.

        Returns
        -------
        dict with ``y_pred_adjusted``
        """
        if estimator is None:
            estimator = LogisticRegression(max_iter=1000, solver="lbfgs")
            estimator.fit(np.asarray(X_train), np.asarray(y_train))

        postprocessor = ThresholdOptimizer(
            estimator=estimator,
            constraints="demographic_parity",
            objective="balanced_accuracy_score",
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

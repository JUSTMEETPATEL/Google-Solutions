"""In-processing: Adversarial Debiasing (MIT-03).

Uses Fairlearn's ExponentiatedGradient as a practical alternative to
TF-based adversarial debiasing — produces a fair classifier directly.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from fairlearn.reductions import DemographicParity, ExponentiatedGradient
from sklearn.linear_model import LogisticRegression

from .base import BaseMitigation


class AdversarialDebiasingMitigation(BaseMitigation):
    """In-processing debiasing via constrained optimization.

    Uses Fairlearn's ``ExponentiatedGradient`` with ``DemographicParity``
    constraint to train a fair classifier. This is a practical substitute
    for TF-based adversarial debiasing that doesn't require TensorFlow.
    """

    name = "adversarial_debiasing"
    category = "in-processing"

    def apply(
        self,
        X_train: np.ndarray | pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray | pd.DataFrame,
        y_test: np.ndarray,
        sensitive_feature: str,
        sensitive_train: pd.Series,
        sensitive_test: pd.Series,
        base_estimator: Any = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Train a debiased model using constrained optimization.

        Parameters
        ----------
        base_estimator : estimator, optional
            sklearn-compatible estimator. Default: ``LogisticRegression``.

        Returns
        -------
        dict with ``model``, ``y_pred_train``, ``y_pred_test``
        """
        estimator = base_estimator or LogisticRegression(
            max_iter=1000, solver="lbfgs"
        )

        mitigator = ExponentiatedGradient(
            estimator=estimator,
            constraints=DemographicParity(),
        )

        mitigator.fit(
            np.asarray(X_train),
            np.asarray(y_train),
            sensitive_features=np.asarray(sensitive_train),
        )

        y_pred_train = mitigator.predict(np.asarray(X_train))
        y_pred_test = mitigator.predict(np.asarray(X_test))

        return {
            "model": mitigator,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
        }

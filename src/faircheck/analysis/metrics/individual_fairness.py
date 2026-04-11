"""Individual Fairness metric (BIAS-06).

Uses cosine distance over non-protected features to verify that
similar individuals receive similar predictions (Lipschitz condition).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from .base import BaseMetric, MetricResult


class IndividualFairnessMetric(BaseMetric):
    """Cosine-distance-based individual fairness (Dwork et al.).

    Measures the fraction of individual pairs that satisfy the Lipschitz
    condition: ``|f(xi) - f(xj)| <= L * d(xi, xj)``.

    ``higher_is_better`` is True (consistency_score >= 0.80 desired).
    """

    name = "individual_fairness"
    default_threshold = 0.80
    higher_is_better = True

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        y_prob: np.ndarray | None = None,
        feature_matrix: np.ndarray | pd.DataFrame | None = None,
        lipschitz_constant: float = 1.0,
        sample_size: int = 1000,
        **kwargs: Any,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold

        if feature_matrix is None:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message=(
                    "Individual fairness requires feature_matrix "
                    "(non-protected features)."
                ),
            )

        if y_prob is None:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Individual fairness requires probability scores (y_prob).",
            )

        X = np.asarray(feature_matrix, dtype=float)
        probs = np.asarray(y_prob, dtype=float)
        n = len(X)

        # Subsample if dataset is large (O(n²) pairwise computation)
        if n > sample_size:
            rng = np.random.default_rng(42)
            indices = rng.choice(n, size=sample_size, replace=False)
            X = X[indices]
            probs = probs[indices]
            n = sample_size

        # Normalize features (D-04: auto-normalization)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Pairwise cosine distance
        sim_matrix = cosine_similarity(X_scaled)
        dist_matrix = 1.0 - sim_matrix

        # Pairwise output distance
        prob_diff = np.abs(probs[:, None] - probs[None, :])

        # Lipschitz consistency: |f(xi) - f(xj)| <= L * d(xi, xj)
        lipschitz_bound = lipschitz_constant * dist_matrix
        consistent = prob_diff <= lipschitz_bound

        # Only count upper triangle (avoid double-counting and diagonal)
        upper_mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        total_pairs = int(upper_mask.sum())
        violations = int((~consistent[upper_mask]).sum())
        consistency_score = (
            1.0 - (violations / total_pairs) if total_pairs > 0 else 1.0
        )

        status = self.evaluate_status(consistency_score, threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(consistency_score),
            threshold=threshold,
            status=status,
            details={
                "consistency_score": float(consistency_score),
                "lipschitz_constant": lipschitz_constant,
                "sample_size": n,
                "violations": violations,
                "total_pairs": total_pairs,
            },
        )

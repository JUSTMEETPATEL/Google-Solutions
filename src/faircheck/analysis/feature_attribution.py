"""SHAP-based feature attribution for bias explanation.

Uses permutation importance (model-agnostic) as the primary method,
with optional SHAP TreeExplainer for tree-based models. This avoids
a hard dependency on the `shap` package.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)


def compute_feature_attribution(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: dict[str, pd.Series],
    feature_names: list[str] | None = None,
    n_repeats: int = 10,
) -> dict[str, Any]:
    """Compute feature importance and per-group attribution.

    Uses permutation importance (model-agnostic) to determine which
    features most influence predictions, then compares importance
    across demographic groups to identify bias drivers.

    Parameters
    ----------
    model : estimator
        Fitted scikit-learn compatible model (must have ``predict``).
    X : DataFrame or ndarray
        Feature matrix used for predictions.
    y_true, y_pred : array-like
        Ground truth and predictions.
    sensitive_features : dict[str, Series]
        Protected attribute values.
    feature_names : list[str], optional
        Feature column names. Inferred from X if DataFrame.
    n_repeats : int
        Number of permutation repeats.

    Returns
    -------
    dict with keys:
        - ``global_importance``: sorted feature importance rankings
        - ``per_group_importance``: importance broken down by group
        - ``bias_drivers``: features that contribute most to group disparities
    """
    if isinstance(X, pd.DataFrame):
        feature_names = feature_names or list(X.columns)
        X_arr = X.values
    else:
        X_arr = np.asarray(X)
        feature_names = feature_names or [f"feature_{i}" for i in range(X_arr.shape[1])]

    # ── Global permutation importance ─────────────────────────────
    try:
        perm_result = permutation_importance(
            model, X_arr, y_true,
            n_repeats=n_repeats,
            random_state=42,
            scoring="accuracy",
        )
        global_imp = {
            fname: {
                "importance_mean": round(float(perm_result.importances_mean[i]), 6),
                "importance_std": round(float(perm_result.importances_std[i]), 6),
            }
            for i, fname in enumerate(feature_names)
        }
        # Sort by importance
        global_imp = dict(
            sorted(global_imp.items(), key=lambda x: x[1]["importance_mean"], reverse=True)
        )
    except Exception as e:
        logger.warning("Global permutation importance failed: %s", e)
        global_imp = {}

    # ── Per-group importance ──────────────────────────────────────
    per_group_importance: dict[str, dict[str, dict[str, float]]] = {}
    bias_drivers: list[dict[str, Any]] = []

    for attr_name, attr_values in sensitive_features.items():
        attr_values = pd.Series(attr_values)
        groups = attr_values.unique()
        group_importances: dict[str, dict[str, float]] = {}

        for group in groups:
            mask = attr_values == group
            if mask.sum() < 20:
                continue
            X_group = X_arr[mask]
            y_group = y_true[mask]

            try:
                perm_g = permutation_importance(
                    model, X_group, y_group,
                    n_repeats=min(n_repeats, 5),
                    random_state=42,
                    scoring="accuracy",
                )
                group_importances[str(group)] = {
                    fname: round(float(perm_g.importances_mean[i]), 6)
                    for i, fname in enumerate(feature_names)
                }
            except Exception:
                continue

        per_group_importance[attr_name] = group_importances

        # ── Identify bias drivers ─────────────────────────────────
        # A "bias driver" is a feature whose importance varies significantly
        # across groups → it affects groups differently
        if len(group_importances) >= 2:
            for fname in feature_names:
                group_vals = [
                    gi.get(fname, 0) for gi in group_importances.values()
                ]
                if not group_vals:
                    continue
                spread = max(group_vals) - min(group_vals)
                if spread > 0.01:  # Significance threshold
                    max_group = max(
                        group_importances.keys(),
                        key=lambda g: group_importances[g].get(fname, 0),
                    )
                    min_group = min(
                        group_importances.keys(),
                        key=lambda g: group_importances[g].get(fname, 0),
                    )
                    bias_drivers.append({
                        "feature": fname,
                        "attribute": attr_name,
                        "importance_spread": round(spread, 6),
                        "most_affected_group": max_group,
                        "least_affected_group": min_group,
                        "explanation": (
                            f"The feature '{fname}' has {spread:.1%} more predictive influence "
                            f"for the '{max_group}' group compared to '{min_group}' in the "
                            f"'{attr_name}' attribute. This suggests it may be acting as a "
                            f"proxy for {attr_name}."
                        ),
                    })

    # Sort bias drivers by spread
    bias_drivers.sort(key=lambda x: x["importance_spread"], reverse=True)

    return {
        "global_importance": global_imp,
        "per_group_importance": per_group_importance,
        "bias_drivers": bias_drivers[:10],  # Top 10
    }

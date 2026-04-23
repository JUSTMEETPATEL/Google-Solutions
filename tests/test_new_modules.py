"""Smoke tests for all new analysis modules."""

from faircheck.analysis.explanations import generate_explanation, generate_all_explanations
from faircheck.analysis.recommend import recommend_mitigation
from faircheck.analysis.drift import compute_drift
from faircheck.analysis.intersectional import compute_intersectional_analysis
from faircheck.analysis.significance import bootstrap_confidence_interval
from faircheck.analysis.feature_attribution import compute_feature_attribution
from faircheck.config import load_config, _deep_merge, DEFAULT_CONFIG

import numpy as np
import pandas as pd


def test_explanations():
    result = generate_explanation(
        "demographic_parity_difference", 0.143, 0.10, "fail", "gender"
    )
    assert result["severity"] == "fail"
    assert "summary" in result
    assert "detail" in result
    assert "recommendation" in result
    assert "14.3%" in result["summary"]
    print("  [PASS] Explanations - fail case")

    result2 = generate_explanation(
        "disparate_impact_ratio", 0.92, 0.80, "pass", "race"
    )
    assert result2["severity"] == "pass"
    print("  [PASS] Explanations - pass case")

    # Test generate_all_explanations
    results = {
        "gender": {
            "metrics": {
                "demographic_parity_difference": {
                    "value": 0.15,
                    "threshold": 0.10,
                    "status": "fail",
                },
                "disparate_impact_ratio": {
                    "value": 0.75,
                    "threshold": 0.80,
                    "status": "fail",
                },
            }
        }
    }
    all_exp = generate_all_explanations(results)
    assert "gender" in all_exp
    assert len(all_exp["gender"]) == 2
    print("  [PASS] Explanations - generate_all")


def test_recommendations():
    analysis = {
        "results": {
            "gender": {
                "metrics": {
                    "demographic_parity_difference": {
                        "value": 0.15, "status": "fail", "threshold": 0.1
                    },
                    "equalized_odds_difference": {
                        "value": 0.12, "status": "fail", "threshold": 0.1
                    },
                }
            }
        }
    }
    recs = recommend_mitigation(analysis)
    assert len(recs) > 0
    assert recs[0]["priority"] == 1
    assert all("algorithm" in r for r in recs)
    print(f"  [PASS] Recommendations - {len(recs)} strategies found")

    # Test all-pass case
    recs2 = recommend_mitigation({
        "results": {
            "gender": {
                "metrics": {
                    "demographic_parity_difference": {
                        "value": 0.03, "status": "pass", "threshold": 0.1
                    }
                }
            }
        }
    })
    assert recs2[0]["algorithm"] == "none"
    print("  [PASS] Recommendations - no mitigation needed")


def test_drift():
    baseline = {
        "overall_risk_level": "medium",
        "results": {
            "gender": {
                "metrics": {
                    "dp": {"value": 0.08, "status": "warning", "threshold": 0.1}
                }
            }
        },
    }
    current = {
        "overall_risk_level": "high",
        "results": {
            "gender": {
                "metrics": {
                    "dp": {"value": 0.15, "status": "fail", "threshold": 0.1}
                }
            }
        },
    }
    drift = compute_drift(baseline, current)
    assert drift["overall_drift"] == "degraded"
    assert drift["risk_change"] == "worsened"
    assert len(drift["alerts"]) == 1
    assert "summary" in drift
    print("  [PASS] Drift - degradation detected")


def test_intersectional():
    np.random.seed(42)
    n = 200
    y_true = np.random.randint(0, 2, n)
    y_pred = np.random.randint(0, 2, n)
    sf = {
        "gender": pd.Series(np.random.choice(["male", "female"], n)),
        "race": pd.Series(np.random.choice(["white", "black", "asian"], n)),
    }
    result = compute_intersectional_analysis(y_true, y_pred, sf)
    assert "intersections" in result
    assert len(result["intersections"]) > 0
    print(f"  [PASS] Intersectional - {len(result['intersections'])} intersection(s)")


def test_significance():
    np.random.seed(42)
    n = 200
    y_true = np.random.randint(0, 2, n)
    y_pred = np.random.randint(0, 2, n)
    sf = pd.Series(np.random.choice(["A", "B"], n))

    from faircheck.analysis.metrics import DemographicParityMetric
    metric = DemographicParityMetric()
    ci = bootstrap_confidence_interval(
        y_true, y_pred, sf, metric, n_bootstrap=100
    )
    assert ci["point_estimate"] is not None
    assert ci["ci_lower"] is not None
    assert ci["ci_upper"] is not None
    assert ci["ci_lower"] <= ci["ci_upper"]
    print(f"  [PASS] Significance - CI: [{ci['ci_lower']:.4f}, {ci['ci_upper']:.4f}]")


def test_feature_attribution():
    from sklearn.ensemble import RandomForestClassifier

    np.random.seed(42)
    n = 100
    X = pd.DataFrame({
        "feat_a": np.random.randn(n),
        "feat_b": np.random.randn(n),
        "feat_c": np.random.randn(n),
    })
    y = (X["feat_a"] > 0).astype(int).values

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)
    y_pred = clf.predict(X)

    sf = {"gender": pd.Series(np.random.choice(["M", "F"], n))}
    result = compute_feature_attribution(
        clf, X, y, y_pred, sf, n_repeats=3
    )
    assert "global_importance" in result
    assert len(result["global_importance"]) == 3
    print(f"  [PASS] Attribution - {len(result['global_importance'])} features ranked")


def test_config_deep_merge():
    user = {"metrics": {"default_thresholds": {"demographic_parity_difference": 0.05}}}
    merged = _deep_merge(DEFAULT_CONFIG, user)
    assert merged["metrics"]["default_thresholds"]["demographic_parity_difference"] == 0.05
    assert merged["metrics"]["default_thresholds"]["equalized_odds_difference"] == 0.10
    assert merged["metrics"]["warning_factor"] == 0.8
    print("  [PASS] Config - deep merge preserves defaults")


if __name__ == "__main__":
    print("\n=== FairCheck New Module Tests ===\n")
    test_explanations()
    test_recommendations()
    test_drift()
    test_intersectional()
    test_significance()
    test_feature_attribution()
    test_config_deep_merge()
    print("\n=== All tests passed! ===\n")

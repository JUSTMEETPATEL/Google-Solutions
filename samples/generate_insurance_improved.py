import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path

OUT_DIR = Path(__file__).parent

def _print_summary(name: str, df: pd.DataFrame, target: str, protected: list[str], model, X):
    """Print a formatted summary for a generated sample."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Rows: {len(df)} | Target: '{target}' | Features: {list(X.columns)}")
    print(f"  Protected attrs: {protected}")
    print(f"  Overall positive rate: {df[target].mean():.2%}")
    for attr in protected:
        print(f"  --- {attr} ---")
        for group in sorted(df[attr].unique()):
            subset = df[df[attr] == group]
            rate = subset[target].mean()
            print(f"    {group:>20s}: {rate:.2%}  (n={len(subset)})")
    print(f"  Model accuracy: {model.score(X.values, df[target].values):.2%}")
    print()

def generate_insurance_improved():
    np.random.seed(505)  # Same seed to keep base features identical
    n = 650

    gender = np.random.choice(["Male", "Female", "Non-binary"], n, p=[0.48, 0.48, 0.04])
    age = np.random.randint(21, 75, n)
    age_group = pd.cut(age, bins=[0, 30, 50, 100], labels=["Young", "Middle", "Senior"]).astype(str)
    claim_amount = np.random.lognormal(8.5, 1, n).clip(500, 200_000).astype(int)
    policy_tenure_years = np.random.exponential(5, n).clip(0, 30).astype(int)
    num_prior_claims = np.random.poisson(1.2, n).clip(0, 10)
    coverage_level = np.random.choice([1, 2, 3], n, p=[0.30, 0.45, 0.25])  # Basic/Standard/Premium
    has_documentation = np.random.choice([0, 1], n, p=[0.15, 0.85])
    risk_score = np.random.normal(50, 15, n).clip(0, 100).astype(int)

    # REMOVED BIAS: Fair generation of claim_approved purely based on merit factors
    score = (
        -0.000015 * claim_amount
        + 0.12 * policy_tenure_years
        - 0.25 * num_prior_claims
        + 0.5 * coverage_level
        + 1.5 * has_documentation
        - 0.02 * risk_score
    )
    
    # We remove the bias terms completely to simulate a fair dataset/process
    bias = 0.0
    
    prob = 1 / (1 + np.exp(-(score + bias - 0.5)))
    claim_approved = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "gender": gender,
        "age_group": age_group,
        "claim_amount": claim_amount,
        "policy_tenure_years": policy_tenure_years,
        "num_prior_claims": num_prior_claims,
        "coverage_level": coverage_level,
        "has_documentation": has_documentation,
        "risk_score": risk_score,
        "claim_approved": claim_approved,
    })

    X = df[["claim_amount", "policy_tenure_years", "num_prior_claims",
            "coverage_level", "has_documentation", "risk_score"]]
    y = df["claim_approved"]

    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=505)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "insurance_claims_improved_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "insurance_claims_improved_model.pkl")
    _print_summary("Insurance — Claim Approval (Improved - Unbiased)", df, "claim_approved",
                   ["gender", "age_group"], model, X)

if __name__ == "__main__":
    print("Generating FairCheck improved sample dataset & model...\n")
    generate_insurance_improved()
    print(f"\n{'='*60}")
    print(f"  Improved files saved to: {OUT_DIR.resolve()}")
    print(f"{'='*60}")

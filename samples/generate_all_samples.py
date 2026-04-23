"""Generate multiple realistic sample datasets + models for FairCheck demos.

Each scenario targets a different domain and bias type:
  1. lending_credit     — Race bias in credit approval
  2. healthcare_triage  — Age bias in emergency triage priority
  3. criminal_recidivism — Race+gender bias in recidivism prediction
  4. education_admission — Socioeconomic + ethnicity bias in college admissions
  5. insurance_claims   — Gender + age bias in insurance claim approval
  6. hiring_promotion   — Gender + race intersectional bias in promotions

Usage:
    python samples/generate_all_samples.py
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
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


# ─────────────────────────────────────────────────────────────
# 1. LENDING — Race bias in credit approval
# ─────────────────────────────────────────────────────────────
def generate_lending():
    np.random.seed(101)
    n = 800

    race = np.random.choice(
        ["White", "Black", "Hispanic", "Asian"],
        size=n, p=[0.45, 0.25, 0.20, 0.10],
    )
    credit_score = np.random.normal(680, 60, n).clip(300, 850).astype(int)
    annual_income = np.random.lognormal(10.8, 0.6, n).clip(15_000, 500_000).astype(int)
    debt_to_income = np.random.beta(2, 5, n) * 0.7  # 0–0.7 range
    loan_amount = np.random.lognormal(11, 0.5, n).clip(5_000, 1_000_000).astype(int)
    employment_years = np.random.exponential(6, n).clip(0, 40).astype(int)
    has_bankruptcy = np.random.choice([0, 1], n, p=[0.92, 0.08])

    # Bias: Black and Hispanic applicants get subtly penalized
    score = (
        0.008 * credit_score
        + 0.000005 * annual_income
        - 3.0 * debt_to_income
        + 0.05 * employment_years
        - 1.2 * has_bankruptcy
        - 0.0000003 * loan_amount
    )
    bias_map = {"White": 0.4, "Asian": 0.3, "Black": -0.7, "Hispanic": -0.5}
    bias = np.array([bias_map[r] for r in race])
    prob = 1 / (1 + np.exp(-(score + bias - 3.5)))
    approved = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "race": race,
        "credit_score": credit_score,
        "annual_income": annual_income,
        "debt_to_income": debt_to_income.round(3),
        "loan_amount": loan_amount,
        "employment_years": employment_years,
        "has_bankruptcy": has_bankruptcy,
        "approved": approved,
    })

    X = df[["credit_score", "annual_income", "debt_to_income",
            "loan_amount", "employment_years", "has_bankruptcy"]]
    y = df["approved"]

    model = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=101)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "lending_credit_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "lending_credit_model.pkl")
    _print_summary("Lending — Credit Approval (Race Bias)", df, "approved", ["race"], model, X)


# ─────────────────────────────────────────────────────────────
# 2. HEALTHCARE — Age bias in triage priority
# ─────────────────────────────────────────────────────────────
def generate_healthcare():
    np.random.seed(202)
    n = 600

    age = np.random.randint(18, 90, n)
    age_group = pd.cut(age, bins=[0, 35, 55, 100], labels=["Young", "Middle", "Senior"]).astype(str)
    gender = np.random.choice(["Male", "Female"], n, p=[0.48, 0.52])
    systolic_bp = np.random.normal(130, 20, n).clip(80, 220).astype(int)
    heart_rate = np.random.normal(80, 15, n).clip(40, 180).astype(int)
    oxygen_sat = np.random.normal(96, 3, n).clip(70, 100).round(1)
    pain_level = np.random.randint(0, 11, n)  # 0-10 scale
    num_comorbidities = np.random.poisson(1.5, n).clip(0, 8)
    is_emergency = np.random.choice([0, 1], n, p=[0.7, 0.3])

    # Bias: Seniors get systematically lower priority even when vitals are worse
    score = (
        0.03 * (systolic_bp - 120)
        + 0.03 * (heart_rate - 70)
        - 0.15 * (oxygen_sat - 97)
        + 0.25 * pain_level
        + 0.5 * num_comorbidities
        + 2.0 * is_emergency
    )
    age_bias = np.where(age_group == "Senior", -1.0,
               np.where(age_group == "Middle", 0.0, 0.5))
    prob = 1 / (1 + np.exp(-(score + age_bias - 1.5)))
    high_priority = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "age_group": age_group,
        "gender": gender,
        "systolic_bp": systolic_bp,
        "heart_rate": heart_rate,
        "oxygen_saturation": oxygen_sat,
        "pain_level": pain_level,
        "num_comorbidities": num_comorbidities,
        "is_emergency": is_emergency,
        "high_priority": high_priority,
    })

    X = df[["systolic_bp", "heart_rate", "oxygen_saturation",
            "pain_level", "num_comorbidities", "is_emergency"]]
    y = df["high_priority"]

    model = RandomForestClassifier(n_estimators=80, max_depth=6, random_state=202)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "healthcare_triage_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "healthcare_triage_model.pkl")
    _print_summary("Healthcare — Triage Priority (Age Bias)", df, "high_priority",
                   ["age_group", "gender"], model, X)


# ─────────────────────────────────────────────────────────────
# 3. CRIMINAL JUSTICE — Race + gender bias in recidivism
# ─────────────────────────────────────────────────────────────
def generate_recidivism():
    np.random.seed(303)
    n = 1000

    race = np.random.choice(
        ["White", "Black", "Hispanic"],
        size=n, p=[0.40, 0.35, 0.25],
    )
    gender = np.random.choice(["Male", "Female"], n, p=[0.78, 0.22])
    age_at_release = np.random.normal(35, 10, n).clip(18, 70).astype(int)
    prior_convictions = np.random.poisson(2.5, n).clip(0, 15)
    sentence_length_months = np.random.exponential(24, n).clip(1, 240).astype(int)
    has_substance_abuse = np.random.choice([0, 1], n, p=[0.55, 0.45])
    has_employment = np.random.choice([0, 1], n, p=[0.60, 0.40])
    education_level = np.random.choice([0, 1, 2, 3], n, p=[0.25, 0.40, 0.25, 0.10])
    # 0=No HS, 1=HS, 2=Some College, 3=Degree

    # Bias: Black individuals labeled as higher recidivism risk, males penalized
    score = (
        -0.03 * age_at_release
        + 0.4 * prior_convictions
        + 0.005 * sentence_length_months
        + 0.8 * has_substance_abuse
        - 0.6 * has_employment
        - 0.3 * education_level
    )
    race_bias = {"White": -0.5, "Black": 0.9, "Hispanic": 0.3}
    gender_bias = {"Male": 0.3, "Female": -0.4}
    bias = np.array([race_bias[r] + gender_bias[g] for r, g in zip(race, gender)])
    prob = 1 / (1 + np.exp(-(score + bias - 0.5)))
    recidivism = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "race": race,
        "gender": gender,
        "age_at_release": age_at_release,
        "prior_convictions": prior_convictions,
        "sentence_length_months": sentence_length_months,
        "has_substance_abuse": has_substance_abuse,
        "has_employment": has_employment,
        "education_level": education_level,
        "recidivism": recidivism,
    })

    X = df[["age_at_release", "prior_convictions", "sentence_length_months",
            "has_substance_abuse", "has_employment", "education_level"]]
    y = df["recidivism"]

    model = LogisticRegression(max_iter=1000, random_state=303)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "criminal_recidivism_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "criminal_recidivism_model.pkl")
    _print_summary("Criminal Justice — Recidivism (Race+Gender Bias)", df, "recidivism",
                   ["race", "gender"], model, X)


# ─────────────────────────────────────────────────────────────
# 4. EDUCATION — Socioeconomic + ethnicity bias in admissions
# ─────────────────────────────────────────────────────────────
def generate_education():
    np.random.seed(404)
    n = 700

    ethnicity = np.random.choice(
        ["White", "Asian", "Black", "Hispanic", "Indigenous"],
        size=n, p=[0.40, 0.20, 0.18, 0.17, 0.05],
    )
    family_income_bracket = np.random.choice(
        ["Low", "Medium", "High"], n, p=[0.35, 0.40, 0.25],
    )
    gpa = np.random.normal(3.2, 0.5, n).clip(1.0, 4.0).round(2)
    sat_score = np.random.normal(1100, 150, n).clip(400, 1600).astype(int)
    extracurriculars = np.random.poisson(3, n).clip(0, 10)
    ap_courses = np.random.poisson(2.5, n).clip(0, 12)
    legacy_status = np.random.choice([0, 1], n, p=[0.85, 0.15])
    first_generation = np.random.choice([0, 1], n, p=[0.65, 0.35])

    # Bias: wealth and ethnicity affect admission disproportionately
    income_map = {"Low": 0, "Medium": 1, "High": 2}
    income_encoded = np.array([income_map[i] for i in family_income_bracket])

    score = (
        1.5 * gpa
        + 0.003 * sat_score
        + 0.2 * extracurriculars
        + 0.25 * ap_courses
        + 0.5 * legacy_status
        - 0.2 * first_generation  # slight penalty for first-gen (systemic)
    )
    eth_bias = {"White": 0.3, "Asian": -0.2, "Black": -0.6,
                "Hispanic": -0.4, "Indigenous": -0.5}
    income_bias = income_encoded * 0.4  # richer = more advantage
    bias = np.array([eth_bias[e] for e in ethnicity]) + income_bias
    prob = 1 / (1 + np.exp(-(score + bias - 7.5)))
    admitted = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "ethnicity": ethnicity,
        "family_income_bracket": family_income_bracket,
        "gpa": gpa,
        "sat_score": sat_score,
        "extracurriculars": extracurriculars,
        "ap_courses": ap_courses,
        "legacy_status": legacy_status,
        "first_generation": first_generation,
        "admitted": admitted,
    })

    # Encode categorical for model training
    income_num = np.array([income_map[i] for i in family_income_bracket])
    df_model = df.copy()
    df_model["income_encoded"] = income_num

    X = df_model[["gpa", "sat_score", "extracurriculars",
                   "ap_courses", "legacy_status", "first_generation", "income_encoded"]]
    y = df["admitted"]

    model = DecisionTreeClassifier(max_depth=8, random_state=404)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    # Save CSV with encoded income for model compatibility
    df["income_encoded"] = income_num
    df.to_csv(OUT_DIR / "education_admission_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "education_admission_model.pkl")
    _print_summary("Education — College Admission (Ethnicity+Income Bias)", df, "admitted",
                   ["ethnicity", "family_income_bracket"], model, X)


# ─────────────────────────────────────────────────────────────
# 5. INSURANCE — Gender + age bias in claim approval
# ─────────────────────────────────────────────────────────────
def generate_insurance():
    np.random.seed(505)
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

    # Bias: Females and young people have lower claim approval
    score = (
        -0.000015 * claim_amount
        + 0.12 * policy_tenure_years
        - 0.25 * num_prior_claims
        + 0.5 * coverage_level
        + 1.5 * has_documentation
        - 0.02 * risk_score
    )
    gender_bias_map = {"Male": 0.4, "Female": -0.5, "Non-binary": -0.3}
    age_bias = np.where(age_group == "Young", -0.6,
               np.where(age_group == "Senior", 0.2, 0.1))
    bias = np.array([gender_bias_map[g] for g in gender]) + age_bias
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

    model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=505)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "insurance_claims_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "insurance_claims_model.pkl")
    _print_summary("Insurance — Claim Approval (Gender+Age Bias)", df, "claim_approved",
                   ["gender", "age_group"], model, X)


# ─────────────────────────────────────────────────────────────
# 6. HIRING — Gender + race intersectional bias in promotions
# ─────────────────────────────────────────────────────────────
def generate_promotions():
    np.random.seed(606)
    n = 900

    gender = np.random.choice(["Male", "Female"], n, p=[0.55, 0.45])
    race = np.random.choice(
        ["White", "Black", "Asian", "Hispanic"],
        size=n, p=[0.50, 0.20, 0.18, 0.12],
    )
    years_at_company = np.random.exponential(5, n).clip(1, 25).astype(int)
    performance_rating = np.random.normal(3.5, 0.8, n).clip(1.0, 5.0).round(1)
    projects_completed = np.random.poisson(8, n).clip(0, 30)
    certifications = np.random.poisson(1.5, n).clip(0, 8)
    team_size_managed = np.random.choice([0, 0, 0, 3, 5, 8, 12, 20], n)
    education_level = np.random.choice([1, 2, 3, 4], n, p=[0.10, 0.35, 0.40, 0.15])
    # 1=HS, 2=Bachelors, 3=Masters, 4=PhD
    hours_overtime_monthly = np.random.exponential(8, n).clip(0, 60).astype(int)

    # Intersectional bias: White males get promoted more;
    # Women of color face the steepest penalties
    score = (
        0.12 * years_at_company
        + 0.6 * performance_rating
        + 0.04 * projects_completed
        + 0.15 * certifications
        + 0.02 * team_size_managed
        + 0.2 * education_level
        + 0.01 * hours_overtime_monthly
    )
    gender_bias_map = {"Male": 0.5, "Female": -0.3}
    race_bias_map = {"White": 0.4, "Asian": 0.0, "Black": -0.6, "Hispanic": -0.4}
    # Intersectional penalty: women of color get double disadvantage
    intersect_penalty = np.where(
        (np.isin(race, ["Black", "Hispanic"])) & (gender == "Female"),
        -0.4, 0.0
    )
    bias = (np.array([gender_bias_map[g] for g in gender]) +
            np.array([race_bias_map[r] for r in race]) +
            intersect_penalty)
    prob = 1 / (1 + np.exp(-(score + bias - 4.5)))
    promoted = (np.random.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "gender": gender,
        "race": race,
        "years_at_company": years_at_company,
        "performance_rating": performance_rating,
        "projects_completed": projects_completed,
        "certifications": certifications,
        "team_size_managed": team_size_managed,
        "education_level": education_level,
        "hours_overtime_monthly": hours_overtime_monthly,
        "promoted": promoted,
    })

    X = df[["years_at_company", "performance_rating", "projects_completed",
            "certifications", "team_size_managed", "education_level",
            "hours_overtime_monthly"]]
    y = df["promoted"]

    model = RandomForestClassifier(n_estimators=120, max_depth=7, random_state=606)
    model.fit(X, y)
    model.feature_names_in_ = np.array(list(X.columns))

    df.to_csv(OUT_DIR / "hiring_promotion_data.csv", index=False)
    joblib.dump(model, OUT_DIR / "hiring_promotion_model.pkl")
    _print_summary("Hiring — Promotion Decisions (Gender+Race Intersectional Bias)", df, "promoted",
                   ["gender", "race"], model, X)


# ─────────────────────────────────────────────────────────────
# Run all generators
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating FairCheck sample datasets & models...\n")
    generate_lending()
    generate_healthcare()
    generate_recidivism()
    generate_education()
    generate_insurance()
    generate_promotions()
    print(f"\n{'='*60}")
    print(f"  All files saved to: {OUT_DIR.resolve()}")
    print(f"{'='*60}")

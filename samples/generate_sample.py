"""Generate sample hiring model + dataset for FairCheck demo."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path

np.random.seed(42)
n = 500

gender = np.random.choice(["Male", "Female"], size=n, p=[0.5, 0.5])
age = np.random.randint(22, 60, size=n)
experience = np.random.randint(0, 30, size=n)
education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
education = np.random.choice(list(education_map.keys()), size=n)
education_encoded = np.array([education_map[e] for e in education])

# Introduce gender bias: males get hired more often
score = 0.3 * experience + 0.5 * education_encoded + 0.01 * age
bias = np.where(gender == "Male", 0.8, -0.3)
prob = 1 / (1 + np.exp(-(score + bias - 4)))
hired = (np.random.random(n) < prob).astype(int)

df = pd.DataFrame({
    "gender": gender,
    "age": age,
    "experience": experience,
    "education_level": education_encoded,
    "hired": hired,
})

out_dir = Path(__file__).parent
df.to_csv(out_dir / "hiring_data.csv", index=False)

# Train a model (on features only, not on gender directly)
X = df[["age", "experience", "education_level"]].values
y = df["hired"].values
model = LogisticRegression(max_iter=1000)
model.fit(X, y)
model.feature_names_in_ = np.array(["age", "experience", "education_level"])
joblib.dump(model, out_dir / "hiring_model.pkl")

print(f"Dataset: {len(df)} rows, overall hire rate: {hired.mean():.2%}")
print(f"  Male hire rate:   {df[df.gender == 'Male'].hired.mean():.2%}")
print(f"  Female hire rate: {df[df.gender == 'Female'].hired.mean():.2%}")
print(f"Model accuracy: {model.score(X, y):.2%}")
print(f"Files saved to: {out_dir.resolve()}")

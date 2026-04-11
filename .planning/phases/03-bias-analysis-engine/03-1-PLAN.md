---
phase: 03
plan: 1
title: "Core Fairness Metrics & Domain Guidance"
wave: 1
depends_on: []
files_modified:
  - src/faircheck/analysis/__init__.py
  - src/faircheck/analysis/metrics/__init__.py
  - src/faircheck/analysis/metrics/base.py
  - src/faircheck/analysis/metrics/demographic_parity.py
  - src/faircheck/analysis/metrics/equalized_odds.py
  - src/faircheck/analysis/metrics/disparate_impact.py
  - src/faircheck/analysis/metrics/predictive_parity.py
  - src/faircheck/analysis/metrics/calibration.py
  - src/faircheck/analysis/metrics/individual_fairness.py
  - src/faircheck/analysis/domains.py
  - src/faircheck/config.py
requirements: [BIAS-01, BIAS-02, BIAS-03, BIAS-04, BIAS-05, BIAS-06, BIAS-07, BIAS-09]
autonomous: true
---

# Plan 03-1: Core Fairness Metrics & Domain Guidance

<objective>
Implement the 6 core fairness metric classes with self-evaluating threshold logic, the BaseMetric ABC, and the domain guidance module. Each metric computes its value and evaluates pass/warning/fail status internally (D-03). Domain guidance is hardcoded in dictionaries (D-01).
</objective>

<must_haves>
- All 6 metrics compute correctly against known values
- Each metric self-evaluates pass/warning/fail status using the threshold + warning_factor logic (D-03, D-05)
- Small subgroups (< 30 samples) return null with a warning (D-02)
- Domain guidance returns correct metric recommendations for hiring, lending, healthcare (D-01)
- Disparate Impact Ratio uses inverted threshold logic (higher is better)
- Individual fairness uses cosine distance with auto-selected non-protected features (D-04)
</must_haves>

## Tasks

<task id="03-1-1" title="Create MetricResult dataclass and BaseMetric ABC">
<read_first>
- src/faircheck/algorithms/base.py (existing ABC pattern to follow)
- src/faircheck/config.py (threshold structure in DEFAULT_CONFIG)
</read_first>

<action>
Create `src/faircheck/analysis/__init__.py` (empty, just the package marker).

Create `src/faircheck/analysis/metrics/__init__.py` that exports all metric classes:
```python
from .base import BaseMetric, MetricResult
from .demographic_parity import DemographicParityMetric
from .equalized_odds import EqualizedOddsMetric
from .disparate_impact import DisparateImpactMetric
from .predictive_parity import PredictiveParityMetric
from .calibration import CalibrationMetric
from .individual_fairness import IndividualFairnessMetric

__all__ = [
    "BaseMetric", "MetricResult",
    "DemographicParityMetric", "EqualizedOddsMetric",
    "DisparateImpactMetric", "PredictiveParityMetric",
    "CalibrationMetric", "IndividualFairnessMetric",
]
```

Create `src/faircheck/analysis/metrics/base.py` with:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import numpy as np
import pandas as pd

MIN_SUBGROUP_SIZE = 30

@dataclass
class MetricResult:
    name: str
    value: float | None
    threshold: float
    status: str  # "pass" | "warning" | "fail" | "skipped"
    details: dict[str, Any] = field(default_factory=dict)
    warning_message: str | None = None

class BaseMetric(ABC):
    name: str
    default_threshold: float
    higher_is_better: bool = False  # Most metrics: lower diff = fairer

    @abstractmethod
    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs,
    ) -> MetricResult:
        ...

    def evaluate_status(
        self, value: float, threshold: float, warning_factor: float = 0.8
    ) -> str:
        if self.higher_is_better:
            warning_bound = threshold + (1.0 - threshold) * (1.0 - warning_factor)
            if value >= warning_bound:
                return "pass"
            elif value >= threshold:
                return "warning"
            else:
                return "fail"
        else:
            warning_bound = threshold * warning_factor
            if value <= warning_bound:
                return "pass"
            elif value <= threshold:
                return "warning"
            else:
                return "fail"

    def _check_subgroup_size(
        self, sensitive_features: pd.Series
    ) -> dict[str, str | None]:
        warnings = {}
        for group_name, group_size in sensitive_features.value_counts().items():
            if group_size < MIN_SUBGROUP_SIZE:
                warnings[str(group_name)] = (
                    f"Subgroup '{group_name}' has {group_size} samples "
                    f"(min: {MIN_SUBGROUP_SIZE}). Metric may be unreliable."
                )
        return warnings
```
</action>

<acceptance_criteria>
- `src/faircheck/analysis/metrics/base.py` contains `class BaseMetric(ABC)` with `evaluate_status` method
- `src/faircheck/analysis/metrics/base.py` contains `class MetricResult` with fields: `name`, `value`, `threshold`, `status`, `details`, `warning_message`
- `src/faircheck/analysis/metrics/base.py` contains `MIN_SUBGROUP_SIZE = 30`
- `evaluate_status` for `higher_is_better=False`: value 0.05 with threshold 0.10 and warning_factor 0.8 returns "pass" (0.05 <= 0.08)
- `evaluate_status` for `higher_is_better=False`: value 0.09 with threshold 0.10 and warning_factor 0.8 returns "warning" (0.08 < 0.09 <= 0.10)
- `evaluate_status` for `higher_is_better=True`: value 0.95 with threshold 0.80 and warning_factor 0.8 returns "pass"
- `src/faircheck/analysis/metrics/__init__.py` imports all 6 metric classes
</acceptance_criteria>
</task>

<task id="03-1-2" title="Implement Demographic Parity metric">
<read_first>
- src/faircheck/analysis/metrics/base.py (BaseMetric ABC to subclass)
</read_first>

<action>
Create `src/faircheck/analysis/metrics/demographic_parity.py`:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
from fairlearn.metrics import demographic_parity_difference, selection_rate
from fairlearn.metrics import MetricFrame
from .base import BaseMetric, MetricResult, MIN_SUBGROUP_SIZE

class DemographicParityMetric(BaseMetric):
    name = "demographic_parity_difference"
    default_threshold = 0.10
    higher_is_better = False

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        value = demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )

        # Per-group selection rates
        mf = MetricFrame(
            metrics=selection_rate,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        by_group = mf.by_group.to_dict()

        status = self.evaluate_status(abs(value), threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "difference": float(abs(value)),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )
```
</action>

<acceptance_criteria>
- `demographic_parity.py` contains `class DemographicParityMetric(BaseMetric)`
- `DemographicParityMetric.name` equals `"demographic_parity_difference"`
- `DemographicParityMetric.default_threshold` equals `0.10`
- Class uses `fairlearn.metrics.demographic_parity_difference` for computation
- Returns `MetricResult` with `details["by_group"]` dict containing per-group selection rates
</acceptance_criteria>
</task>

<task id="03-1-3" title="Implement Equalized Odds metric">
<read_first>
- src/faircheck/analysis/metrics/base.py
- src/faircheck/analysis/metrics/demographic_parity.py (pattern to follow)
</read_first>

<action>
Create `src/faircheck/analysis/metrics/equalized_odds.py`:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
from fairlearn.metrics import (
    equalized_odds_difference,
    true_positive_rate,
    false_positive_rate,
    MetricFrame,
)
from .base import BaseMetric, MetricResult

class EqualizedOddsMetric(BaseMetric):
    name = "equalized_odds_difference"
    default_threshold = 0.10
    higher_is_better = False

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        value = equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensitive_features
        )

        mf = MetricFrame(
            metrics={"tpr": true_positive_rate, "fpr": false_positive_rate},
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        by_group = mf.by_group.to_dict()

        status = self.evaluate_status(abs(value), threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "tpr_difference": float(mf.difference()["tpr"]),
                "fpr_difference": float(mf.difference()["fpr"]),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )
```
</action>

<acceptance_criteria>
- `equalized_odds.py` contains `class EqualizedOddsMetric(BaseMetric)`
- Uses `fairlearn.metrics.equalized_odds_difference` for top-level value
- Returns per-group TPR and FPR breakdowns in `details["by_group"]`
- Returns `tpr_difference` and `fpr_difference` in details
</acceptance_criteria>
</task>

<task id="03-1-4" title="Implement Disparate Impact Ratio metric">
<read_first>
- src/faircheck/analysis/metrics/base.py
</read_first>

<action>
Create `src/faircheck/analysis/metrics/disparate_impact.py`:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame, selection_rate
from .base import BaseMetric, MetricResult

class DisparateImpactMetric(BaseMetric):
    name = "disparate_impact_ratio"
    default_threshold = 0.80
    higher_is_better = True  # Ratio >= 0.80 is desired

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        mf = MetricFrame(
            metrics=selection_rate,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        by_group = mf.by_group.to_dict()
        group_rates = list(by_group.values())

        if len(group_rates) < 2 or max(group_rates) == 0:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Cannot compute ratio: fewer than 2 groups or max rate is 0.",
            )

        value = min(group_rates) / max(group_rates)
        status = self.evaluate_status(value, threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "ratio": float(value),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )
```
</action>

<acceptance_criteria>
- `disparate_impact.py` contains `class DisparateImpactMetric(BaseMetric)`
- `higher_is_better` is `True`
- `default_threshold` is `0.80`
- Computes ratio as `min(group_rates) / max(group_rates)`
- Returns `status="skipped"` when fewer than 2 groups or max rate is 0
</acceptance_criteria>
</task>

<task id="03-1-5" title="Implement Predictive Parity metric">
<read_first>
- src/faircheck/analysis/metrics/base.py
</read_first>

<action>
Create `src/faircheck/analysis/metrics/predictive_parity.py`:

```python
from __future__ import annotations
import functools
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score
from fairlearn.metrics import MetricFrame
from .base import BaseMetric, MetricResult

class PredictiveParityMetric(BaseMetric):
    name = "predictive_parity"
    default_threshold = 0.10
    higher_is_better = False

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        precision_fn = functools.partial(precision_score, zero_division=0)
        mf = MetricFrame(
            metrics=precision_fn,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )

        by_group = mf.by_group.to_dict()
        value = float(mf.difference())

        status = self.evaluate_status(abs(value), threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=value,
            threshold=threshold,
            status=status,
            details={
                "by_group": by_group,
                "difference": float(abs(value)),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )
```
</action>

<acceptance_criteria>
- `predictive_parity.py` contains `class PredictiveParityMetric(BaseMetric)`
- Computes precision per group using `MetricFrame` with `sklearn.metrics.precision_score`
- Uses `functools.partial(precision_score, zero_division=0)` to handle empty groups
- Returns per-group precision values in `details["by_group"]`
</acceptance_criteria>
</task>

<task id="03-1-6" title="Implement Calibration by Group metric">
<read_first>
- src/faircheck/analysis/metrics/base.py
</read_first>

<action>
Create `src/faircheck/analysis/metrics/calibration.py`:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
from .base import BaseMetric, MetricResult, MIN_SUBGROUP_SIZE

class CalibrationMetric(BaseMetric):
    name = "calibration_by_group"
    default_threshold = 0.05
    higher_is_better = False

    @staticmethod
    def _expected_calibration_error(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
    ) -> float:
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        total = len(y_true)
        if total == 0:
            return 0.0
        for i in range(n_bins):
            mask = (y_prob > bin_edges[i]) & (y_prob <= bin_edges[i + 1])
            if i == 0:
                mask = (y_prob >= bin_edges[i]) & (y_prob <= bin_edges[i + 1])
            bin_count = mask.sum()
            if bin_count == 0:
                continue
            bin_acc = y_true[mask].mean()
            bin_conf = y_prob[mask].mean()
            ece += (bin_count / total) * abs(bin_acc - bin_conf)
        return float(ece)

    def compute(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.Series,
        threshold: float | None = None,
        warning_factor: float = 0.8,
        y_prob: np.ndarray | None = None,
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold
        subgroup_warnings = self._check_subgroup_size(sensitive_features)

        if y_prob is None:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Calibration requires probability scores (y_prob). Model does not support predict_proba.",
            )

        y_true_arr = np.asarray(y_true)
        y_prob_arr = np.asarray(y_prob)
        sf = pd.Series(sensitive_features)

        group_ece = {}
        for group_name in sf.unique():
            mask = sf == group_name
            group_size = mask.sum()
            if group_size < MIN_SUBGROUP_SIZE:
                group_ece[str(group_name)] = None
                continue
            group_ece[str(group_name)] = self._expected_calibration_error(
                y_true_arr[mask], y_prob_arr[mask]
            )

        valid_eces = [v for v in group_ece.values() if v is not None]
        if len(valid_eces) < 2:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Not enough valid groups for calibration comparison.",
            )

        value = max(valid_eces) - min(valid_eces)
        status = self.evaluate_status(value, threshold, warning_factor)

        return MetricResult(
            name=self.name,
            value=float(value),
            threshold=threshold,
            status=status,
            details={
                "by_group": group_ece,
                "difference": float(value),
            },
            warning_message=(
                "; ".join(subgroup_warnings.values()) if subgroup_warnings else None
            ),
        )
```
</action>

<acceptance_criteria>
- `calibration.py` contains `class CalibrationMetric(BaseMetric)`
- `default_threshold` is `0.05`
- Contains `_expected_calibration_error` static method with n_bins parameter
- Returns `status="skipped"` when `y_prob` is None
- Returns `status="skipped"` when fewer than 2 groups have enough samples
- Computes calibration difference as `max(group_eces) - min(group_eces)`
</acceptance_criteria>
</task>

<task id="03-1-7" title="Implement Individual Fairness metric">
<read_first>
- src/faircheck/analysis/metrics/base.py
</read_first>

<action>
Create `src/faircheck/analysis/metrics/individual_fairness.py`:

```python
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from .base import BaseMetric, MetricResult

class IndividualFairnessMetric(BaseMetric):
    name = "individual_fairness"
    default_threshold = 0.80  # Consistency score >= 0.80 is desired
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
        **kwargs,
    ) -> MetricResult:
        threshold = threshold or self.default_threshold

        if feature_matrix is None:
            return MetricResult(
                name=self.name,
                value=None,
                threshold=threshold,
                status="skipped",
                warning_message="Individual fairness requires feature_matrix (non-protected features).",
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

        # Subsample if dataset is large
        if n > sample_size:
            rng = np.random.default_rng(42)
            indices = rng.choice(n, size=sample_size, replace=False)
            X = X[indices]
            probs = probs[indices]
            n = sample_size

        # Normalize features
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
        consistency_score = 1.0 - (violations / total_pairs) if total_pairs > 0 else 1.0

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
```
</action>

<acceptance_criteria>
- `individual_fairness.py` contains `class IndividualFairnessMetric(BaseMetric)`
- `higher_is_better` is `True`
- Uses `sklearn.metrics.pairwise.cosine_similarity` for distance computation
- Uses `sklearn.preprocessing.StandardScaler` for feature normalization
- Subsamples to `sample_size` when dataset exceeds it (default 1000)
- Returns `status="skipped"` when `feature_matrix` or `y_prob` is None
- Computes `consistency_score` as `1.0 - (violations / total_pairs)`
</acceptance_criteria>
</task>

<task id="03-1-8" title="Create domain guidance module">
<read_first>
- .planning/phases/03-bias-analysis-engine/03-CONTEXT.md (D-01 decision)
- .planning/phases/03-bias-analysis-engine/03-RESEARCH.md (domain guidance structure)
</read_first>

<action>
Create `src/faircheck/analysis/domains.py`:

```python
"""Hardcoded domain guidance dictionaries (D-01).

Maps domain use cases to recommended fairness metrics and rationale.
"""

from __future__ import annotations
from typing import TypedDict

class DomainGuidance(TypedDict):
    recommended_metrics: list[str]
    critical_thresholds: dict[str, float]
    rationale: str
    regulations: list[str]

DOMAIN_GUIDANCE: dict[str, DomainGuidance] = {
    "hiring": {
        "recommended_metrics": [
            "demographic_parity_difference",
            "disparate_impact_ratio",
        ],
        "critical_thresholds": {
            "disparate_impact_ratio": 0.80,
        },
        "rationale": (
            "Employment law (US EEOC, EU AI Act Art. 10) focuses on selection "
            "rate parity. The 4/5ths rule requires disparate impact ratio >= 0.80."
        ),
        "regulations": ["EEOC Guidelines", "EU AI Act Article 10"],
    },
    "lending": {
        "recommended_metrics": [
            "equalized_odds_difference",
            "predictive_parity",
        ],
        "critical_thresholds": {
            "equalized_odds_difference": 0.05,
        },
        "rationale": (
            "Lending compliance (ECOA, EU AI Act) emphasizes equal error rates "
            "across groups to prevent systematically disadvantaging borrowers."
        ),
        "regulations": ["ECOA", "EU AI Act Article 9"],
    },
    "healthcare": {
        "recommended_metrics": [
            "calibration_by_group",
            "equalized_odds_difference",
        ],
        "critical_thresholds": {
            "calibration_by_group": 0.03,
        },
        "rationale": (
            "Healthcare AI (EU AI Act Art. 9) prioritizes calibration so predicted "
            "probabilities match actual outcomes across demographics."
        ),
        "regulations": ["EU AI Act Article 9", "FDA AI/ML Guidelines"],
    },
}

def get_domain_guidance(domain: str | None) -> DomainGuidance | None:
    """Return guidance for the specified domain, or None if unknown."""
    if domain is None:
        return None
    return DOMAIN_GUIDANCE.get(domain.lower())

def list_supported_domains() -> list[str]:
    """Return list of supported domain names."""
    return list(DOMAIN_GUIDANCE.keys())
```
</action>

<acceptance_criteria>
- `domains.py` contains `DOMAIN_GUIDANCE` dict with keys `"hiring"`, `"lending"`, `"healthcare"`
- Each domain has `recommended_metrics`, `critical_thresholds`, `rationale`, `regulations`
- `get_domain_guidance("hiring")` returns the hiring guidance dict
- `get_domain_guidance("unknown")` returns None
- `list_supported_domains()` returns `["hiring", "lending", "healthcare"]`
</acceptance_criteria>
</task>

<task id="03-1-9" title="Extend config.py with Phase 3 defaults">
<read_first>
- src/faircheck/config.py (current DEFAULT_CONFIG structure)
</read_first>

<action>
Update `src/faircheck/config.py` to add Phase 3 thresholds and settings to `DEFAULT_CONFIG`:

Add to the existing `DEFAULT_CONFIG["metrics"]["default_thresholds"]`:
- `"predictive_parity": 0.10`
- `"calibration_by_group": 0.05`
- `"individual_fairness": 0.80`

Add new top-level keys:
```python
"metrics": {
    "default_thresholds": {
        "demographic_parity_difference": 0.10,
        "equalized_odds_difference": 0.10,
        "disparate_impact_ratio": 0.80,
        "predictive_parity": 0.10,
        "calibration_by_group": 0.05,
        "individual_fairness": 0.80,
    },
    "warning_factor": 0.8,
},
"individual_fairness": {
    "lipschitz_constant": 1.0,
    "sample_size": 1000,
},
```

Keep the existing `attributes` and `report` sections untouched.
</action>

<acceptance_criteria>
- `config.py` DEFAULT_CONFIG contains all 6 metric thresholds
- `config.py` DEFAULT_CONFIG contains `"warning_factor": 0.8` under `metrics`
- `config.py` DEFAULT_CONFIG contains `"individual_fairness"` section with `lipschitz_constant` and `sample_size`
- Existing `attributes` and `report` sections are preserved
</acceptance_criteria>
</task>

<verification>
After all tasks complete:
1. All 8 Python files exist under `src/faircheck/analysis/`
2. `python -c "from faircheck.analysis.metrics import DemographicParityMetric, EqualizedOddsMetric, DisparateImpactMetric, PredictiveParityMetric, CalibrationMetric, IndividualFairnessMetric"` exits 0
3. `python -c "from faircheck.analysis.domains import get_domain_guidance; print(get_domain_guidance('hiring'))"` prints the hiring guidance dict
4. `python -c "from faircheck.config import DEFAULT_CONFIG; assert len(DEFAULT_CONFIG['metrics']['default_thresholds']) == 6"` exits 0
</verification>

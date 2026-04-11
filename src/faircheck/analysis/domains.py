"""Hardcoded domain guidance dictionaries (D-01).

Maps domain use cases to recommended fairness metrics and rationale.
"""

from __future__ import annotations

from typing import TypedDict


class DomainGuidance(TypedDict):
    """Structure for a single domain's fairness guidance."""

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

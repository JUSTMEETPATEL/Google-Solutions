import tomllib
from pathlib import Path

DEFAULT_CONFIG = {
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
    "attributes": {
        "protected": ["gender", "race", "age"]
    },
    "report": {
        "format": "pdf"
    }
}

def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override dict into base, preserving base defaults."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path_str: str = ".faircheckrc") -> dict:
    """Load configuration from a TOML file, deep-merged with defaults.

    User-provided values override defaults; unspecified keys retain
    their default values.  This prevents silent loss of thresholds
    when a user only customizes a subset.
    """
    path = Path(path_str)
    if not path.is_file():
        return DEFAULT_CONFIG.copy()

    try:
        with path.open("rb") as f:
            user_config = tomllib.load(f)

        return _deep_merge(DEFAULT_CONFIG, user_config)
    except Exception:
        return DEFAULT_CONFIG.copy()

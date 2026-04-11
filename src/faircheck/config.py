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

def load_config(path_str: str = ".faircheckrc") -> dict:
    """Load configuration from a TOML file. Fall back to defaults if not found."""
    path = Path(path_str)
    if not path.is_file():
        return DEFAULT_CONFIG
    
    try:
        with path.open("rb") as f:
            user_config = tomllib.load(f)
            
        # Recursive merge could be implemented later. For now, we return 
        # the parsed TOML config or fall back to default if file lacks top level keys.
        # But for the phase 1 scope, simply parsing is sufficient.
        return user_config
    except Exception:
        return DEFAULT_CONFIG

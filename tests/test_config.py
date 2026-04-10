import pytest
from faircheck.config import load_config

def test_load_config_with_existing_file(tmp_path):
    # Setup temporary valid toml file
    config_file = tmp_path / ".faircheckrc"
    config_file.write_text('''
[metrics]
default_thresholds = { demographic_parity_difference = 0.15 }
    ''')
    
    config = load_config(str(config_file))
    assert "metrics" in config
    assert "default_thresholds" in config["metrics"]
    assert config["metrics"]["default_thresholds"]["demographic_parity_difference"] == 0.15

def test_load_config_fallback_to_defaults(tmp_path):
    # Provide a path to a non-existent file
    missing_file = tmp_path / "nonexistent.toml"
    config = load_config(str(missing_file))
    
    assert "metrics" in config
    assert config["metrics"]["default_thresholds"]["demographic_parity_difference"] == 0.10
    assert "attributes" in config
    assert config["attributes"]["protected"] == ["gender", "race", "age"]

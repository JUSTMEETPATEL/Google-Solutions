---
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - .faircheckrc
  - src/faircheck/__init__.py
  - src/faircheck/config.py
  - src/faircheck/algorithms/__init__.py
  - src/faircheck/algorithms/base.py
  - src/faircheck/algorithms/fairlearn_wrapper.py
  - src/faircheck/algorithms/aif360_wrapper.py
  - tests/conftest.py
  - tests/test_config.py
  - tests/test_algorithms.py
autonomous: true
---

# Phase 1: Engine Foundation & Project Scaffold - Plan

**Requirements Covered:** ENG-01, ENG-02, ENG-03

## Must Haves
- Python package skeleton is importable locally.
- `uv` is configured to manage dependencies including `pytest`, `fairlearn`, and `aif360`.
- Configuration module parses `.faircheckrc` written in TOML natively.
- Base algorithm class and library-specific wrapper templates exist in `src/`.

<task>
<id>1</id>
<title>Initialize Project Structure and uv Package</title>
<description>Create the basic `src` layout for the `faircheck` Python module, initialize `uv` for python dependencies, and add `pytest` for testing.</description>
<read_first>
- .planning/phases/01/1-CONTEXT.md (to confirm `uv` and `src` layout)
- .planning/phases/01/01-VALIDATION.md (for verification commands)
</read_first>
<action>
1. Run `uv init --lib --python 3.11`. This will generate a `pyproject.toml` and basic structure.
2. Update `pyproject.toml`:
   Set `name = "faircheck"`
   Ensure build-system uses hatchling or similar default.
3. Remove the generic placeholder files created by uv (e.g., `src/faircheck/hello.py`) if present.
4. Rename `src/{package}` to `src/faircheck/` and create an empty `src/faircheck/__init__.py`.
5. Add core testing dependency: `uv add --dev pytest`
6. Run `uv sync` to ensure lockfile is created.
7. Create `tests/conftest.py` with an empty pytest configuration to mark test directory availability.
</action>
<acceptance_criteria>
- `pyproject.toml` contains `name = "faircheck"` and `[project]` configuration.
- `src/faircheck/__init__.py` exists.
- `uv run pytest` executes without fatal configuration errors (can report "no tests collected").
- `uv run python -c "import faircheck"` runs without an ImportError.
</acceptance_criteria>
</task>

<task>
<id>2</id>
<title>Implement TOML Configuration System (.faircheckrc)</title>
<description>Create the `.faircheckrc` standard config file, and a config parser in the code using Python 3.11's built-in `tomllib`.</description>
<read_first>
- src/faircheck/__init__.py
</read_first>
<action>
1. Create a root file named `.faircheckrc` with standard TOML layout:
```toml
[metrics]
default_thresholds = { demographic_parity_difference = 0.10, equalized_odds_difference = 0.10, disparate_impact_ratio = 0.80 }

[attributes]
protected = ["gender", "race", "age"]

[report]
format = "pdf"
```
2. Create `src/faircheck/config.py`.
3. In `config.py`, import `tomllib` and `pathlib.Path`.
4. Create a function `load_config(path_str: str = ".faircheckrc") -> dict:` that opens the file in "rb" mode and calls `tomllib.load()`. If the file doesn't exist, it should return default dict matching above.
5. Create `tests/test_config.py` that asserts `load_config()` correctly parses `[metrics]` keys.
</action>
<acceptance_criteria>
- `.faircheckrc` exists and matches the provided TOML schema.
- `src/faircheck/config.py` contains `def load_config(`.
- `tests/test_config.py` exists with a test verifying `.faircheckrc` loads correctly.
- `uv run pytest tests/test_config.py` exits 0.
</acceptance_criteria>
</task>

<task>
<id>3</id>
<title>Add Core Bias Dependencies and Wrapper Architecture</title>
<description>Install `fairlearn` and `aif360` then scaffold the wrapper Strategy pattern for fairness algorithms to abstract API changes.</description>
<read_first>
- src/faircheck/algorithms/
</read_first>
<action>
1. Run `uv add fairlearn aif360 scikit-learn pandas`.
2. Create `src/faircheck/algorithms/` python package with `__init__.py`.
3. Create `src/faircheck/algorithms/base.py`. Define an abstract base class `class FairnessWrapper(ABC):` using Python's `abc` module. It should define `@abstractmethod`s for `fit(self, X, y, protected_attribute)`, `predict(self, X)`, and `evaluate_fairness(self, dataset)`.
4. Create `src/faircheck/algorithms/fairlearn_wrapper.py`. Define `class FairlearnWrapper(FairnessWrapper):` with stub implementations that raise `NotImplementedError("To be implemented in Phase 3")`.
5. Create `src/faircheck/algorithms/aif360_wrapper.py`. Define `class AIF360Wrapper(FairnessWrapper):` with stub implementations that raise `NotImplementedError("To be implemented in Phase 3")`.
6. Export these three classes in `src/faircheck/algorithms/__init__.py`.
7. Create `tests/test_algorithms.py` that tests that instantiating `FairlearnWrapper` and calling `fit` raises `NotImplementedError`.
</action>
<acceptance_criteria>
- `pyproject.toml` includes `fairlearn`, `aif360`, `scikit-learn`, and `pandas`.
- `src/faircheck/algorithms/base.py` defines `class FairnessWrapper(ABC)`.
- `src/faircheck/algorithms/__init__.py` exposes the wrapper classes.
- `uv run pytest tests/test_algorithms.py` exits 0.
</acceptance_criteria>
</task>

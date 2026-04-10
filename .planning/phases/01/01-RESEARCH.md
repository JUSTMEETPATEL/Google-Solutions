# Phase 1: Engine Foundation & Project Scaffold - Research

**Researched:** 2026-04-10
**Domain:** Python Package Scaffolding, Core Abstractions
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Dependency Management:** Use `uv` (modern, extremely fast dependency resolver and installer).
- **Config Format:** Use `TOML` for `.faircheckrc` (standard for Python tooling).
- **Project Structure:** Use `src/` layout to prevent import errors and properly namespace the `faircheck` module.

### Specifics
- The core wrapper logic will be namespaced under `faircheck.algorithms` to abstract AIF360 and Fairlearn API surfaces.

### Deferred Ideas (OUT OF SCOPE)
- None.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ENG-01 | Engine scaffold with Python 3.11+, pyproject.toml, and test infrastructure | use `uv init --lib`, `pytest` |
| ENG-02 | Abstract wrapper layer around AIF360 and Fairlearn isolating upstream API changes | Use strategy pattern for `faircheck.algorithms` |
| ENG-03 | Config system (.faircheckrc) for thresholds, attributes, report preferences | Use `tomllib` (built-in 3.11+) |
</phase_requirements>

## Summary

This phase establishes the foundational Python backend. Using `uv` for package management provides speed and deterministic resolution. The `src/` layout avoids common Python path issues. The `.faircheckrc` file in TOML will be parsed natively via Python 3.11's `tomllib`.

**Primary recommendation:** Initialize with `uv init --lib --vcs git` and implement a strategy pattern abstracting AIF360/Fairlearn.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `uv` | latest | Package manager | Blazing fast Python dependency management |
| `fairlearn` | >=0.11 | Primary bias lib | Cleaner API than AIF360, backed by Microsoft |
| `aif360` | >=0.6 | Extended algorithms | Contains algorithms missing in fairlearn |
| `pytest` | latest | Testing | Standard for Python testing |

## Architecture Patterns

### Recommended Project Structure
```text
.
├── .faircheckrc          # Global config
├── pyproject.toml        # uv package definitions
└── src/
    └── faircheck/
        ├── __init__.py
        ├── config.py     # Parses .faircheckrc
        └── algorithms/   # Wrappers for AIF360/Fairlearn
            ├── __init__.py
            ├── base.py   # Abstract Base Class for algorithms
            ├── fairlearn_wrapper.py
            └── aif360_wrapper.py
```

### Pattern 1: Strategy Pattern for Algorithms
**What:** Use an Abstract Base Class (ABC) exposing `fit`, `predict`, and `evaluate_fairness`.
**When to use:** To seamlessly swap between Fairlearn and AIF360 algorithms.

## Common Pitfalls

### Pitfall 1: AIF360 Dependencies
**What goes wrong:** AIF360 brings in many heavy/conflicting dependencies (e.g., specific scikit-learn or tensorflow versions).
**How to avoid:** Pin versions carefully to ensure Fairlearn and AIF360 can coexist. Use `uv add aif360 fairlearn scikit-learn pandas`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | pyproject.toml |
| Quick run command | `uv run pytest` |
| Full suite command | `uv run pytest -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ENG-01 | Scaffold exists & valid | smoke | `uv run python -c "import faircheck"` | ❌ |
| ENG-02 | Wrapper exposes API | unit | `uv run pytest tests/test_algorithms.py` | ❌ |
| ENG-03 | Config parses TOML | unit | `uv run pytest tests/test_config.py` | ❌ |

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Strong typing / pydantic (later phases) |


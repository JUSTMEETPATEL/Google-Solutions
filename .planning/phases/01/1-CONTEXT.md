# Phase 1 Context: Engine Foundation & Project Scaffold

**Created:** 2026-04-10

## Decisions

- **Dependency Management:** Use `uv` (modern, extremely fast dependency resolver and installer).
- **Config Format:** Use `TOML` for `.faircheckrc` (standard for Python tooling).
- **Project Structure:** Use `src/` layout to prevent import errors and properly namespace the `faircheck` module.

## Specifics

- The core wrapper logic will be namespaced under `faircheck.algorithms` to abstract AIF360 and Fairlearn API surfaces.

## Canonical Refs

- `.planning/PROJECT.md` (Project Rules and Constraints)
- `.planning/REQUIREMENTS.md` (Phase 1 Requirements)

## Deferred Ideas

- None.

# Phase 1: Engine Foundation & Project Scaffold - Validation Strategy

**Created:** 2026-04-10
**Status:** Generated from RESEARCH.md

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

### Sampling Rate
- **Per task commit:** `uv run pytest`
- **Per wave merge:** `uv run pytest -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_algorithms.py` — covers REQ-ENG-02
- [ ] `tests/test_config.py` — covers REQ-ENG-03
- [ ] `tests/conftest.py` — shared fixtures
- [ ] Framework install: `uv add --dev pytest`

# Phase 10: Regulation Templates — Context

**Status:** Decisions locked
**Date:** 2026-04-11

## Requirements (REG-01 through REG-07)

- REG-01: EU AI Act Article 9 — risk management system documentation
- REG-02: EU AI Act Article 10 — training data governance and bias monitoring
- REG-03: EU AI Act Article 13 — transparency and information provision
- REG-04: EU AI Act Article 14 — human oversight measures (linked to WEB-07)
- REG-05: EU AI Act Article 17 — quality management (audit trail + session history)
- REG-06: Regulatory mapping section cross-references articles
- REG-07: Legal disclaimer

## Decisions

### Architecture
- Extends Phase 7's composable template system
- New Jinja2 section templates under `templates/sections/regulation/`
- A new master template `base_eu_ai_act.html.j2` that includes all standard sections + regulation sections
- `RegulationMapper` class maps analysis results to article requirements
- Risk classification (High/Medium/Low) auto-derived from metric ensemble

### Risk Classification Logic
- High: any metric fails
- Medium: any metric warns, none fail
- Low: all metrics pass

# Phase 07: Report Builder — Context & Decisions

**Phase:** 07-report-builder
**Status:** Decisions locked
**Date:** 2026-04-11

## Requirements

RPT-01 through RPT-11 (11 requirements):
- RPT-01: Cover page (model name, version, audit date, reviewer, regulation standard)
- RPT-02: Executive summary in plain language
- RPT-03: Model card (training data, intended use, limitations)
- RPT-04: Bias analysis results table (threshold, value, status per metric)
- RPT-05: Demographic breakdown charts (per-group performance)
- RPT-06: Mitigation applied section (algorithm, before/after)
- RPT-07: Human oversight record (reviewer, date, decision, signature)
- RPT-08: Appendix with raw metric data and methodology
- RPT-09: PDF output via Jinja2 + WeasyPrint
- RPT-10: Markdown output
- RPT-11: DOCX output via python-docx

## Decisions

### D-01: Template Architecture → Composable Sections
Each report section is its own Jinja2 partial template. A master template
`{% include %}`s them in order. This enables Phase 10 (Regulation Templates)
to swap/extend individual sections without duplicating the entire template.

Structure:
```
src/faircheck/reports/templates/
├── base.html.j2          # Master HTML template (PDF via WeasyPrint)
├── base.md.j2            # Master Markdown template
├── sections/
│   ├── cover.html.j2
│   ├── executive_summary.html.j2
│   ├── model_card.html.j2
│   ├── metrics_table.html.j2
│   ├── demographic_charts.html.j2
│   ├── mitigation.html.j2
│   ├── oversight.html.j2
│   └── appendix.html.j2
└── styles/
    └── report.css
```

### D-02: Chart Rendering → Matplotlib Static Images
Generate PNGs from metric data using Matplotlib. Embed as base64 data URIs
in HTML before WeasyPrint renders to PDF. Works fully offline, no JS dependency.

### D-03: Report Data Contract → Serialized Dict
The report builder accepts a plain dict (from `AnalysisResult.to_dict()` or
stored session JSON). Looser coupling, easier to test with fixture data,
works seamlessly from stored session data in SQLite.

### D-04: DOCX Styling → Minimal
Basic headings, tables, and content for v1. No custom fonts or branded
colors. Get it functional; polish in a later phase.

### D-05: Report Output Location → Session Directory
Reports saved to `~/.faircheck/reports/{session_id}/`. Organized, prevents
cwd clutter. The API and TUI can still copy the file to cwd if requested.

### D-06: Empty Sections → Placeholder Text
Mitigation (RPT-06) and Oversight (RPT-07) sections include placeholder
text ("No mitigation applied" / "No oversight recorded") when data is
absent. Report structure is complete from day 1.

## Dependencies

- Phase 3 (Bias Analysis Engine) — provides `AnalysisResult.to_dict()`
- Phase 5 (Session Persistence) — provides stored session data
- Jinja2 (already installed)
- WeasyPrint (needs install)
- python-docx (needs install)
- matplotlib (needs install)

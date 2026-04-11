---
phase: 07
plan: 1
title: "Report Engine, Templates & Data Contract"
wave: 1
depends_on: []
files_modified:
  - src/faircheck/reports/__init__.py
  - src/faircheck/reports/engine.py
  - src/faircheck/reports/data.py
  - src/faircheck/reports/templates/base.html.j2
  - src/faircheck/reports/templates/base.md.j2
  - src/faircheck/reports/templates/sections/cover.html.j2
  - src/faircheck/reports/templates/sections/executive_summary.html.j2
  - src/faircheck/reports/templates/sections/model_card.html.j2
  - src/faircheck/reports/templates/sections/metrics_table.html.j2
  - src/faircheck/reports/templates/sections/demographic_charts.html.j2
  - src/faircheck/reports/templates/sections/mitigation.html.j2
  - src/faircheck/reports/templates/sections/oversight.html.j2
  - src/faircheck/reports/templates/sections/appendix.html.j2
  - src/faircheck/reports/templates/styles/report.css
requirements: [RPT-01, RPT-02, RPT-03, RPT-04, RPT-05, RPT-06, RPT-07, RPT-08]
autonomous: true
---

# Plan 07-1: Report Engine, Templates & Data Contract

<objective>
Build the report engine core: Jinja2 template loading, the ReportData contract (plain dict input), all 8 HTML section templates, the CSS stylesheet, and the Markdown master template. This is the foundation for all 3 output formats.
</objective>

<must_haves>
- ReportData dataclass that accepts a plain dict (D-03)
- Jinja2 Environment configured with template directory
- 8 HTML section templates matching RPT-01 through RPT-08
- Master HTML template that includes all sections in order
- Master Markdown template for RPT-10
- CSS stylesheet for PDF rendering
- Mitigation and oversight sections show placeholder text when data absent (D-06)
- Report output directory at ~/.faircheck/reports/{session_id}/ (D-05)
</must_haves>

## Tasks

<task id="07-1-1" title="Create ReportData contract and report engine scaffold">
<action>
Create `src/faircheck/reports/__init__.py` with public API exports.

Create `src/faircheck/reports/data.py` — the data contract:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, timezone

@dataclass
class ReportData:
    """Data contract for report generation (D-03).
    
    Accepts a plain dict from AnalysisResult.to_dict() or stored session JSON.
    """
    # Cover page (RPT-01)
    model_name: str = "Unknown Model"
    model_version: str = "1.0"
    audit_date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    reviewer: str = ""
    regulation_standard: str = "EU AI Act"
    
    # Model card (RPT-03)
    training_data_description: str = ""
    intended_use: str = ""
    known_limitations: str = ""
    
    # Analysis results (RPT-04, RPT-05)
    analysis_results: dict[str, Any] = field(default_factory=dict)
    
    # Mitigation (RPT-06) — empty = placeholder shown
    mitigation: dict[str, Any] | None = None
    
    # Oversight (RPT-07) — empty = placeholder shown
    oversight: dict[str, Any] | None = None
    
    # Session metadata
    session_id: str = ""
    
    # Chart images (base64 PNGs, populated by chart module)
    chart_images: dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReportData:
        """Build ReportData from a plain dict."""
        return cls(
            model_name=data.get("model_name", "Unknown Model"),
            model_version=data.get("model_version", "1.0"),
            audit_date=data.get("audit_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            reviewer=data.get("reviewer", ""),
            regulation_standard=data.get("regulation_standard", "EU AI Act"),
            training_data_description=data.get("training_data_description", ""),
            intended_use=data.get("intended_use", ""),
            known_limitations=data.get("known_limitations", ""),
            analysis_results=data.get("analysis_results", {}),
            mitigation=data.get("mitigation"),
            oversight=data.get("oversight"),
            session_id=data.get("session_id", ""),
            chart_images=data.get("chart_images", {}),
        )
```

Create `src/faircheck/reports/engine.py` — the report engine:

```python
from __future__ import annotations
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from faircheck.reports.data import ReportData

logger = logging.getLogger(__name__)
TEMPLATE_DIR = Path(__file__).parent / "templates"

class ReportEngine:
    """Renders reports from ReportData using Jinja2 templates."""
    
    def __init__(self, template_dir: Path | None = None) -> None:
        self.template_dir = template_dir or TEMPLATE_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )
    
    def render_html(self, data: ReportData) -> str:
        """Render the full HTML report (used for PDF generation)."""
        template = self.env.get_template("base.html.j2")
        return template.render(report=data)
    
    def render_markdown(self, data: ReportData) -> str:
        """Render the Markdown report."""
        template = self.env.get_template("base.md.j2")
        return template.render(report=data)
    
    def get_output_dir(self, session_id: str) -> Path:
        """Return report output directory (D-05)."""
        output_dir = Path.home() / ".faircheck" / "reports" / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
```
</action>

<acceptance_criteria>
- `src/faircheck/reports/data.py` contains `ReportData` dataclass with `from_dict` classmethod
- `src/faircheck/reports/engine.py` contains `ReportEngine` with `render_html` and `render_markdown`
- ReportEngine uses Jinja2 `FileSystemLoader` pointed at templates directory
- Output directory defaults to `~/.faircheck/reports/{session_id}/`
</acceptance_criteria>
</task>

<task id="07-1-2" title="Create HTML section templates and CSS">
<action>
Create all template files under `src/faircheck/reports/templates/`:

**`styles/report.css`** — Clean professional styling for PDF:
- A4 page size, professional fonts, clear hierarchy
- Tables with alternating row colors
- Status badges: green (pass), yellow (warning), red (fail)
- Print-friendly margins and page breaks

**`sections/cover.html.j2`** (RPT-01):
Cover page with model name, version, audit date, reviewer, regulation standard.

**`sections/executive_summary.html.j2`** (RPT-02):
Plain language summary: overall risk level, count of pass/warning/fail metrics, top concerns.

**`sections/model_card.html.j2`** (RPT-03):
Training data description, intended use, known limitations. Shows placeholders if empty.

**`sections/metrics_table.html.j2`** (RPT-04):
Table with columns: Metric, Threshold, Value, Status. Iterates over all metrics from analysis_results.

**`sections/demographic_charts.html.j2`** (RPT-05):
Embeds chart images as base64 data URIs. Falls back to table if no charts.

**`sections/mitigation.html.j2`** (RPT-06):
Shows mitigation algorithm and before/after if present, otherwise placeholder (D-06).

**`sections/oversight.html.j2`** (RPT-07):
Shows reviewer name, date, decision if present, otherwise placeholder (D-06).

**`sections/appendix.html.j2`** (RPT-08):
Raw metric values, methodology notes, computation details.

**`base.html.j2`** — Master HTML template:
```html
<!DOCTYPE html>
<html>
<head><style>{% include "styles/report.css" %}</style></head>
<body>
{% include "sections/cover.html.j2" %}
{% include "sections/executive_summary.html.j2" %}
{% include "sections/model_card.html.j2" %}
{% include "sections/metrics_table.html.j2" %}
{% include "sections/demographic_charts.html.j2" %}
{% include "sections/mitigation.html.j2" %}
{% include "sections/oversight.html.j2" %}
{% include "sections/appendix.html.j2" %}
</body>
</html>
```

**`base.md.j2`** — Markdown equivalent of all sections.
</action>

<acceptance_criteria>
- All 8 section templates exist under `templates/sections/`
- `base.html.j2` includes all 8 sections via `{% include %}`
- `base.md.j2` renders equivalent content in Markdown
- `styles/report.css` contains A4 page layout and status badge styling
- Mitigation and oversight templates conditionally show placeholder text
</acceptance_criteria>
</task>

<verification>
1. `python -c "from faircheck.reports.engine import ReportEngine; print('OK')"` exits 0
2. `python -c "from faircheck.reports.data import ReportData; r = ReportData.from_dict({}); print(r.model_name)"` prints "Unknown Model"
</verification>

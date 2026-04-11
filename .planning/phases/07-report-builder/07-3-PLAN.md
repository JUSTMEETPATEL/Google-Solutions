---
phase: 07
plan: 3
title: "PDF, Markdown & DOCX Renderers + Tests"
wave: 2
depends_on: [07-1, 07-2]
files_modified:
  - src/faircheck/reports/renderers.py
  - tests/reports/__init__.py
  - tests/reports/test_renderers.py
  - tests/reports/test_data.py
  - pyproject.toml
requirements: [RPT-09, RPT-10, RPT-11]
autonomous: true
---

# Plan 07-3: PDF, Markdown & DOCX Renderers + Tests

<objective>
Implement the three output format renderers (PDF via WeasyPrint, Markdown file, DOCX via python-docx) and comprehensive tests. Add new dependencies to pyproject.toml.
</objective>

<must_haves>
- PDF renderer: HTML → WeasyPrint → PDF file
- Markdown renderer: template → .md file
- DOCX renderer: python-docx document with headings, tables, content
- All renderers save to ~/.faircheck/reports/{session_id}/ (D-05)
- Dependencies added to pyproject.toml: weasyprint, python-docx, matplotlib
- Tests verify all 3 formats generate without error
</must_haves>

## Tasks

<task id="07-3-1" title="Create renderers for PDF, MD, DOCX">
<read_first>
- src/faircheck/reports/engine.py
- src/faircheck/reports/data.py
- src/faircheck/reports/charts.py
</read_first>

<action>
Create `src/faircheck/reports/renderers.py`:

```python
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
from faircheck.reports.data import ReportData
from faircheck.reports.engine import ReportEngine
from faircheck.reports.charts import generate_charts

logger = logging.getLogger(__name__)

class ReportBuilder:
    """High-level API for generating reports in all formats."""
    
    def __init__(self, engine: ReportEngine | None = None) -> None:
        self.engine = engine or ReportEngine()
    
    def build(
        self,
        data: dict[str, Any],
        formats: list[str] | None = None,
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate reports in requested formats.
        
        Parameters
        ----------
        data : dict
            Plain dict (from AnalysisResult.to_dict() or stored session).
        formats : list[str]
            Output formats: "pdf", "md", "docx". Default: ["pdf"].
        output_dir : Path, optional
            Override output directory. Default: ~/.faircheck/reports/{session_id}/
        
        Returns
        -------
        dict[str, Path]
            Mapping of format → output file path.
        """
        formats = formats or ["pdf"]
        report_data = ReportData.from_dict(data)
        
        # Generate charts and attach to report data
        if report_data.analysis_results:
            report_data.chart_images = generate_charts(report_data.analysis_results)
        
        out_dir = output_dir or self.engine.get_output_dir(
            report_data.session_id or "default"
        )
        
        results = {}
        for fmt in formats:
            if fmt == "pdf":
                results["pdf"] = self._render_pdf(report_data, out_dir)
            elif fmt == "md":
                results["md"] = self._render_md(report_data, out_dir)
            elif fmt == "docx":
                results["docx"] = self._render_docx(report_data, out_dir)
            else:
                logger.warning("Unknown format '%s', skipping", fmt)
        
        return results
    
    def _render_pdf(self, data: ReportData, out_dir: Path) -> Path:
        from weasyprint import HTML
        html_content = self.engine.render_html(data)
        out_path = out_dir / f"faircheck-report.pdf"
        HTML(string=html_content).write_pdf(str(out_path))
        logger.info("PDF report saved: %s", out_path)
        return out_path
    
    def _render_md(self, data: ReportData, out_dir: Path) -> Path:
        md_content = self.engine.render_markdown(data)
        out_path = out_dir / f"faircheck-report.md"
        out_path.write_text(md_content, encoding="utf-8")
        logger.info("Markdown report saved: %s", out_path)
        return out_path
    
    def _render_docx(self, data: ReportData, out_dir: Path) -> Path:
        from docx import Document
        from docx.shared import Inches
        
        doc = Document()
        
        # Cover (RPT-01)
        doc.add_heading("AI Bias Audit Report", level=0)
        doc.add_paragraph(f"Model: {data.model_name} (v{data.model_version})")
        doc.add_paragraph(f"Audit Date: {data.audit_date}")
        if data.reviewer:
            doc.add_paragraph(f"Reviewer: {data.reviewer}")
        doc.add_paragraph(f"Regulation: {data.regulation_standard}")
        
        # Executive Summary (RPT-02)
        doc.add_heading("Executive Summary", level=1)
        risk = data.analysis_results.get("overall_risk_level", "unknown")
        doc.add_paragraph(f"Overall Risk Level: {risk.upper()}")
        
        # Model Card (RPT-03)
        doc.add_heading("Model Card", level=1)
        doc.add_paragraph(data.training_data_description or "Not provided.")
        doc.add_paragraph(f"Intended Use: {data.intended_use or 'Not specified.'}")
        doc.add_paragraph(f"Known Limitations: {data.known_limitations or 'None documented.'}")
        
        # Metrics Table (RPT-04)
        doc.add_heading("Bias Analysis Results", level=1)
        results = data.analysis_results.get("results", {})
        for attr_name, attr_data in results.items():
            doc.add_heading(f"Protected Attribute: {attr_name}", level=2)
            metrics = attr_data.get("metrics", {})
            if metrics:
                table = doc.add_table(rows=1, cols=4)
                table.style = "Table Grid"
                hdr = table.rows[0].cells
                hdr[0].text = "Metric"
                hdr[1].text = "Threshold"
                hdr[2].text = "Value"
                hdr[3].text = "Status"
                for m_name, m_data in metrics.items():
                    row = table.add_row().cells
                    row[0].text = m_name.replace("_", " ").title()
                    row[1].text = str(m_data.get("threshold", ""))
                    row[2].text = str(m_data.get("value", "N/A"))
                    row[3].text = m_data.get("status", "").upper()
        
        # Mitigation (RPT-06)
        doc.add_heading("Mitigation Applied", level=1)
        if data.mitigation:
            doc.add_paragraph(f"Algorithm: {data.mitigation.get('algorithm', 'N/A')}")
        else:
            doc.add_paragraph("No mitigation has been applied to this model.")
        
        # Oversight (RPT-07)
        doc.add_heading("Human Oversight", level=1)
        if data.oversight:
            doc.add_paragraph(f"Reviewer: {data.oversight.get('reviewer', '')}")
            doc.add_paragraph(f"Decision: {data.oversight.get('decision', '')}")
        else:
            doc.add_paragraph("No human oversight decision has been recorded.")
        
        # Appendix (RPT-08)
        doc.add_heading("Appendix: Raw Data & Methodology", level=1)
        doc.add_paragraph("Metrics computed using FairCheck v0.1.0")
        doc.add_paragraph("Libraries: Fairlearn, AIF360, scikit-learn")
        
        out_path = out_dir / f"faircheck-report.docx"
        doc.save(str(out_path))
        logger.info("DOCX report saved: %s", out_path)
        return out_path
```

Update `src/faircheck/reports/__init__.py`:
```python
from faircheck.reports.data import ReportData
from faircheck.reports.engine import ReportEngine
from faircheck.reports.renderers import ReportBuilder
from faircheck.reports.charts import generate_charts

__all__ = ["ReportData", "ReportEngine", "ReportBuilder", "generate_charts"]
```
</action>

<acceptance_criteria>
- `renderers.py` contains `ReportBuilder` with `build()` method
- `build()` accepts formats list and returns dict of output paths
- PDF renderer uses WeasyPrint
- DOCX renderer uses python-docx with tables for metrics
- All renderers save to `~/.faircheck/reports/{session_id}/`
</acceptance_criteria>
</task>

<task id="07-3-2" title="Add dependencies to pyproject.toml">
<action>
Add to pyproject.toml dependencies:
- `weasyprint>=62`
- `python-docx>=1.1.0`
- `matplotlib>=3.8.0`
</action>

<acceptance_criteria>
- pyproject.toml includes weasyprint, python-docx, matplotlib
- `pip install -e .` installs all new dependencies
</acceptance_criteria>
</task>

<task id="07-3-3" title="Write tests for report generation">
<action>
Create `tests/reports/__init__.py` and `tests/reports/test_renderers.py`:

Tests should use a fixture that creates a mock analysis result dict and verify:
1. ReportData.from_dict() correctly parses all fields
2. ReportEngine.render_html() returns valid HTML string
3. ReportEngine.render_markdown() returns valid markdown string
4. ReportBuilder.build(formats=["md"]) creates a .md file
5. ReportBuilder.build(formats=["docx"]) creates a .docx file
6. Charts generate without error from sample data
7. Empty mitigation/oversight produces placeholder text in output
</action>

<acceptance_criteria>
- `pytest tests/reports/ -v` passes all tests
- Tests cover ReportData, ReportEngine, ReportBuilder, and charts
</acceptance_criteria>
</task>

<verification>
1. `python -c "from faircheck.reports import ReportBuilder; print('OK')"` exits 0
2. `pytest tests/reports/ -v` all tests pass
3. `pytest tests/ -v` no regressions
</verification>

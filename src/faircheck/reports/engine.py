"""Report rendering engine — Jinja2 template loader and renderer."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from faircheck.reports.data import ReportData

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"


class ReportEngine:
    """Renders reports from :class:`ReportData` using Jinja2 templates."""

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

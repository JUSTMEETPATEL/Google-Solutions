"""Report rendering engine — Jinja2 template loader and renderer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

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

    def render_html(
        self, data: ReportData, regulation: str | None = None, **extra: Any
    ) -> str:
        """Render the full HTML report (used for PDF generation).

        Parameters
        ----------
        regulation : str, optional
            Regulation standard key (e.g. ``"eu_ai_act"``).  When set,
            uses the regulation-specific master template and injects
            a ``regulation_report`` context variable.
        """
        ctx = self._build_context(data, regulation, extra)
        tpl_name = f"base_{regulation}.html.j2" if regulation else "base.html.j2"
        template = self.env.get_template(tpl_name)
        return template.render(**ctx)

    def render_markdown(
        self, data: ReportData, regulation: str | None = None, **extra: Any
    ) -> str:
        """Render the Markdown report."""
        ctx = self._build_context(data, regulation, extra)
        tpl_name = f"base_{regulation}.md.j2" if regulation else "base.md.j2"
        template = self.env.get_template(tpl_name)
        return template.render(**ctx)

    def _build_context(
        self, data: ReportData, regulation: str | None, extra: dict
    ) -> dict[str, Any]:
        ctx: dict[str, Any] = {"report": data, **extra}
        if regulation:
            from faircheck.reports.regulation import RegulationMapper
            mapper = RegulationMapper()
            ctx["regulation_report"] = mapper.map(data)
        return ctx

    def get_output_dir(self, session_id: str) -> Path:
        """Return report output directory (D-05)."""
        output_dir = Path.home() / ".faircheck" / "reports" / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

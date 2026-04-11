"""FairCheck Report Generation.

Public API:
    - :class:`ReportBuilder` — generate reports in PDF/MD/DOCX
    - :class:`ReportData` — typed data contract for reports
    - :class:`ReportEngine` — Jinja2 template rendering engine
    - :func:`generate_charts` — Matplotlib chart generation
"""

from faircheck.reports.charts import generate_charts
from faircheck.reports.data import ReportData
from faircheck.reports.engine import ReportEngine
from faircheck.reports.renderers import ReportBuilder

__all__ = [
    "ReportBuilder",
    "ReportData",
    "ReportEngine",
    "generate_charts",
]

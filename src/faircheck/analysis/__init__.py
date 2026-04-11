"""FairCheck Bias Analysis Engine.

Public API:
    - :class:`BiasAnalyzer` — orchestrate a full bias scan
    - :class:`AnalysisResult` — structured scan output
    - :func:`compute_performance_breakdown` — per-group metrics
    - :func:`get_domain_guidance` / :func:`list_supported_domains` — domain helpers
"""

from faircheck.analysis.breakdown import compute_performance_breakdown
from faircheck.analysis.domains import get_domain_guidance, list_supported_domains
from faircheck.analysis.engine import AnalysisResult, BiasAnalyzer

__all__ = [
    "AnalysisResult",
    "BiasAnalyzer",
    "compute_performance_breakdown",
    "get_domain_guidance",
    "list_supported_domains",
]

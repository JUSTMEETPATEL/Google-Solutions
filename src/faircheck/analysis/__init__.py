"""FairCheck Bias Analysis Engine.

Public API:
    - :class:`BiasAnalyzer` — orchestrate a full bias scan
    - :class:`AnalysisResult` — structured scan output
    - :func:`compute_performance_breakdown` — per-group metrics
    - :func:`get_domain_guidance` / :func:`list_supported_domains` — domain helpers
    - :func:`compute_intersectional_analysis` — pairwise attribute intersections
    - :func:`compute_all_confidence_intervals` — bootstrap CIs
    - :func:`generate_all_explanations` — plain-English metric explanations
    - :func:`compute_feature_attribution` — permutation importance
    - :func:`compute_drift` — temporal drift monitoring
    - :func:`recommend_mitigation` — auto-recommend algorithms
"""

from faircheck.analysis.breakdown import compute_performance_breakdown
from faircheck.analysis.domains import get_domain_guidance, list_supported_domains
from faircheck.analysis.drift import compute_drift
from faircheck.analysis.engine import AnalysisResult, BiasAnalyzer
from faircheck.analysis.explanations import generate_all_explanations
from faircheck.analysis.feature_attribution import compute_feature_attribution
from faircheck.analysis.intersectional import compute_intersectional_analysis
from faircheck.analysis.recommend import recommend_mitigation
from faircheck.analysis.significance import compute_all_confidence_intervals

__all__ = [
    "AnalysisResult",
    "BiasAnalyzer",
    "compute_all_confidence_intervals",
    "compute_drift",
    "compute_feature_attribution",
    "compute_intersectional_analysis",
    "compute_performance_breakdown",
    "generate_all_explanations",
    "get_domain_guidance",
    "list_supported_domains",
    "recommend_mitigation",
]

"""FairCheck Mitigation Pipeline.

Public API:
    - :class:`MitigationPipeline` — run mitigation with before/after comparison
    - :class:`MitigationResult` — result container
    - :func:`list_algorithms` — list available algorithms
    - :func:`get_algorithm` — get algorithm by name
"""

from faircheck.mitigation.base import BaseMitigation, MitigationResult
from faircheck.mitigation.pipeline import (
    MitigationPipeline,
    get_algorithm,
    list_algorithms,
)

__all__ = [
    "BaseMitigation",
    "MitigationPipeline",
    "MitigationResult",
    "get_algorithm",
    "list_algorithms",
]

"""Scan data cache — persists model + dataset for post-scan mitigation.

After a scan, the uploaded model and dataset are cached to
``~/.faircheck/cache/{session_id}/`` so that mitigation algorithms can
re-load them and actually execute (rather than just recording the choice).
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".faircheck" / "cache"


def cache_scan_artifacts(
    session_id: str,
    model_path: Path,
    dataset_path: Path,
    feature_names: list[str],
    protected_cols: list[str],
    target_col: str,
) -> Path:
    """Cache model + dataset files and metadata for later mitigation.

    Copies temp files into the cache directory before they are cleaned up.
    """
    session_dir = CACHE_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Copy files to cache
    cached_model = session_dir / f"model{model_path.suffix}"
    cached_dataset = session_dir / f"dataset{dataset_path.suffix}"

    shutil.copy2(model_path, cached_model)
    shutil.copy2(dataset_path, cached_dataset)

    # Store metadata
    meta = {
        "feature_names": feature_names,
        "protected_cols": protected_cols,
        "target_col": target_col,
        "model_suffix": model_path.suffix,
        "dataset_suffix": dataset_path.suffix,
    }
    (session_dir / "meta.json").write_text(json.dumps(meta))

    logger.info("Cached scan artifacts for session %s", session_id)
    return session_dir


def load_cached_artifacts(session_id: str) -> dict[str, Any] | None:
    """Load cached model + dataset paths and metadata.

    Returns
    -------
    dict or None
        Keys: ``model_path``, ``dataset_path``, ``feature_names``,
        ``protected_cols``, ``target_col``.  None if cache is missing.
    """
    session_dir = CACHE_DIR / session_id
    meta_file = session_dir / "meta.json"

    if not meta_file.exists():
        return None

    meta = json.loads(meta_file.read_text())
    model_path = session_dir / f"model{meta['model_suffix']}"
    dataset_path = session_dir / f"dataset{meta['dataset_suffix']}"

    if not model_path.exists() or not dataset_path.exists():
        return None

    return {
        "model_path": model_path,
        "dataset_path": dataset_path,
        "feature_names": meta["feature_names"],
        "protected_cols": meta["protected_cols"],
        "target_col": meta["target_col"],
    }


def clear_cache(session_id: str) -> None:
    """Remove cached artifacts for a session."""
    session_dir = CACHE_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
        logger.info("Cleared cache for session %s", session_id)

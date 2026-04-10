"""Chunked dataset loading with type inference and protected attribute detection."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Generator

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

# Regex pattern for likely protected attribute column names.
_PROTECTED_PATTERN = re.compile(
    r"(?i)(gender|sex|race|ethnicity|age|religion|disability)"
)


class DatasetChunker:
    """Load datasets in chunks with automatic type inference and
    protected attribute detection.

    Supports CSV, JSON (line-delimited), and Parquet formats.

    Parameters
    ----------
    filepath : str | Path
        Path to the dataset file.
    chunksize : int
        Number of rows per chunk (default 100 000).
    protected_attributes : dict | None
        Manual overrides mapping column name → attribute label.
        Example: ``{"col_name": "race"}``.
    type_overrides : dict | None
        Manual overrides mapping column name → pandas dtype string.
        Example: ``{"age": "category"}``.
    """

    def __init__(
        self,
        filepath: str | Path,
        chunksize: int = 100_000,
        protected_attributes: dict[str, str] | None = None,
        type_overrides: dict[str, str] | None = None,
    ) -> None:
        self.filepath = Path(filepath)
        self.chunksize = chunksize
        self.protected_overrides = protected_attributes or {}
        self.type_overrides = type_overrides or {}

        suffix = self.filepath.suffix.lower()
        if suffix not in (".csv", ".json", ".parquet"):
            raise ValueError(
                f"Unsupported file format '{suffix}'. "
                "Supported: .csv, .json, .parquet"
            )
        self._suffix = suffix

        # Populated on first chunk.
        self.detected_protected_attributes: dict[str, float] = {}
        self.inferred_types: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Protected attribute heuristics
    # ------------------------------------------------------------------

    def _detect_protected_attributes(
        self, df: pd.DataFrame
    ) -> dict[str, float]:
        """Score each column for likelihood of being a protected attribute.

        Scoring rules
        -------------
        +0.5  if the column name matches the regex pattern.
        +0.4  if the column is string/object/category with 2–10 unique values.

        Returns a dict of ``{column_name: confidence}`` for columns with
        confidence ≥ 0.8.
        """
        results: dict[str, float] = {}

        for col in df.columns:
            score = 0.0

            # Rule 1 – name match.
            if _PROTECTED_PATTERN.search(str(col)):
                score += 0.5

            # Rule 2 – low-cardinality categorical.
            col_dtype = df[col].dtype
            is_string_like = (
                col_dtype == object
                or isinstance(col_dtype, pd.CategoricalDtype)
                or isinstance(col_dtype, pd.StringDtype)
                or str(col_dtype) == "string"
            )
            if is_string_like:
                nunique = df[col].nunique()
                if 2 <= nunique <= 10:
                    score += 0.4

            if score >= 0.8:
                results[col] = round(score, 2)
                logger.info(
                    "Auto-detected protected attribute '%s' "
                    "(confidence=%.2f)",
                    col,
                    score,
                )

        return results

    # ------------------------------------------------------------------
    # Type inference
    # ------------------------------------------------------------------

    def _infer_types(self, df: pd.DataFrame) -> dict[str, str]:
        """Classify each column as numeric, categorical, or binary."""
        types: dict[str, str] = {}
        for col in df.columns:
            if col in self.type_overrides:
                types[col] = self.type_overrides[col]
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                nunique = df[col].nunique()
                if nunique == 2:
                    types[col] = "binary"
                else:
                    types[col] = "numeric"
            else:
                types[col] = "categorical"
        return types

    # ------------------------------------------------------------------
    # Chunk iteration
    # ------------------------------------------------------------------

    def iter_chunks(self) -> Generator[pd.DataFrame, None, None]:
        """Yield dataframe chunks from the underlying file.

        Before yielding, each chunk is validated for NaN values (raises
        ``ValueError`` if any are found) and scanned for protected
        attributes on the first chunk.
        """
        first_chunk = True

        for chunk in self._raw_chunks():
            # Apply type overrides.
            for col, dtype in self.type_overrides.items():
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(dtype)

            # Strict NaN validation.
            if chunk.isnull().values.any():
                nan_cols = [
                    col
                    for col in chunk.columns
                    if chunk[col].isnull().any()
                ]
                raise ValueError(
                    f"Data contains NaN values in column(s): {nan_cols}. "
                    "Clean your dataset before loading into FairCheck."
                )

            # Protected attribute detection & type inference on first chunk.
            if first_chunk:
                self.detected_protected_attributes = (
                    self._detect_protected_attributes(chunk)
                )
                # Merge manual overrides (they always win).
                for col, label in self.protected_overrides.items():
                    self.detected_protected_attributes[col] = 1.0

                self.inferred_types = self._infer_types(chunk)
                first_chunk = False

            yield chunk

    def _raw_chunks(self) -> Generator[pd.DataFrame, None, None]:
        """Dispatch to the correct format-specific reader."""
        if self._suffix == ".csv":
            yield from self._read_csv()
        elif self._suffix == ".json":
            yield from self._read_json()
        elif self._suffix == ".parquet":
            yield from self._read_parquet()

    def _read_csv(self) -> Generator[pd.DataFrame, None, None]:
        reader = pd.read_csv(self.filepath, chunksize=self.chunksize)
        yield from reader

    def _read_json(self) -> Generator[pd.DataFrame, None, None]:
        reader = pd.read_json(
            self.filepath, lines=True, chunksize=self.chunksize
        )
        yield from reader

    def _read_parquet(self) -> Generator[pd.DataFrame, None, None]:
        pf = pq.ParquetFile(self.filepath)
        for batch in pf.iter_batches(batch_size=self.chunksize):
            yield batch.to_pandas()

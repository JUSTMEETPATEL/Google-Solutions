"""High-level ingestion pipeline that binds a model to a dataset."""

from __future__ import annotations

import logging
from pathlib import Path

from faircheck.ingestion.datasets import DatasetChunker
from faircheck.ingestion.models import (
    ModelAdapter,
    ONNXAdapter,
    ScikitLearnAdapter,
)

logger = logging.getLogger(__name__)

# Extensions handled by each adapter.
_SKLEARN_EXTS = {".pkl", ".joblib"}
_ONNX_EXTS = {".onnx"}


class IngestionPipeline:
    """Facade that loads a model + dataset and validates schema alignment.

    Usage
    -----
    >>> pipeline = IngestionPipeline()
    >>> result = pipeline.load("model.pkl", "data.csv")
    >>> result.model.predict(next(result.dataset.iter_chunks()))
    """

    def load(
        self,
        model_path: str | Path,
        data_path: str | Path,
        type_overrides: dict[str, str] | None = None,
        protected_overrides: dict[str, str] | None = None,
    ) -> "IngestionResult":
        """Load a model and dataset, validating schema compatibility.

        Parameters
        ----------
        model_path : str | Path
            Path to the serialized model file (.pkl, .joblib, .onnx).
        data_path : str | Path
            Path to the dataset file (.csv, .json, .parquet).
        type_overrides : dict | None
            Column → dtype overrides for the dataset.
        protected_overrides : dict | None
            Column → attribute-label overrides for protected attributes.

        Returns
        -------
        IngestionResult
            Contains the loaded ``model`` adapter and ``dataset`` chunker.

        Raises
        ------
        ValueError
            If the model file extension is unsupported or if the dataset
            columns do not match the model's expected features.
        """
        model_path = Path(model_path)
        data_path = Path(data_path)

        # --- Load model ---
        model = self._load_model(model_path)

        # --- Load dataset ---
        dataset = DatasetChunker(
            filepath=data_path,
            protected_attributes=protected_overrides,
            type_overrides=type_overrides,
        )

        # --- Schema validation via first-chunk peek ---
        self._validate_schema(model, dataset)

        return IngestionResult(model=model, dataset=dataset)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_model(model_path: Path) -> ModelAdapter:
        ext = model_path.suffix.lower()
        if ext in _SKLEARN_EXTS:
            logger.info("Loading scikit-learn model from %s", model_path)
            return ScikitLearnAdapter(model_path)
        if ext in _ONNX_EXTS:
            logger.info("Loading ONNX model from %s", model_path)
            return ONNXAdapter(model_path)
        raise ValueError(
            f"Unsupported model format '{ext}'. "
            f"Supported: {sorted(_SKLEARN_EXTS | _ONNX_EXTS)}"
        )

    @staticmethod
    def _validate_schema(
        model: ModelAdapter, dataset: DatasetChunker
    ) -> None:
        """Peek at the first chunk and compare columns to the model."""
        expected = model.feature_names_in_
        if expected is None:
            logger.info(
                "Model does not expose feature names — "
                "skipping schema validation."
            )
            return

        # Peek at the first chunk (resets the iterator afterwards).
        first_chunk_iter = dataset.iter_chunks()
        try:
            first_chunk = next(first_chunk_iter)
        except StopIteration:
            raise ValueError("Dataset is empty — no rows to validate.")

        actual = set(first_chunk.columns)
        expected_set = set(expected)

        missing = expected_set - actual
        extra = actual - expected_set

        if missing:
            raise ValueError(
                f"Schema mismatch: model expects columns {sorted(missing)} "
                f"which are missing from the dataset. "
                f"Dataset columns: {sorted(actual)}"
            )

        if extra:
            logger.warning(
                "Dataset has extra columns not used by the model: %s. "
                "They will be ignored during prediction.",
                sorted(extra),
            )


class IngestionResult:
    """Container returned by :meth:`IngestionPipeline.load`."""

    __slots__ = ("model", "dataset")

    def __init__(
        self, model: ModelAdapter, dataset: DatasetChunker
    ) -> None:
        self.model = model
        self.dataset = dataset

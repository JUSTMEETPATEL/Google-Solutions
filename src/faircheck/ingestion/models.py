"""Model adapters providing a unified predict interface across formats."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import onnxruntime as ort
import pandas as pd


class ModelAdapter(ABC):
    """Abstract base class for model adapters.

    All model formats (.pkl, .joblib, .onnx) are wrapped behind this
    interface so downstream bias analysis only calls ``predict()`` and
    ``predict_proba()`` without caring about the underlying runtime.
    """

    @property
    @abstractmethod
    def feature_names_in_(self) -> list[str] | None:
        """Return the feature names the model expects, or None if unknown."""

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return class predictions for *X*."""

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray | None:
        """Return class-probability predictions, or None if unsupported."""


class ScikitLearnAdapter(ModelAdapter):
    """Adapter for scikit-learn models stored as ``.pkl`` or ``.joblib``.

    Uses :func:`joblib.load` which handles both pickle and joblib formats.
    """

    def __init__(self, model_path: str | Path) -> None:
        self._model_path = Path(model_path)
        self._model: Any = joblib.load(self._model_path)

    @property
    def feature_names_in_(self) -> list[str] | None:
        names = getattr(self._model, "feature_names_in_", None)
        if names is not None:
            return list(names)
        return None

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self._model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray | None:
        fn = getattr(self._model, "predict_proba", None)
        if fn is None:
            return None
        return fn(X)


class ONNXAdapter(ModelAdapter):
    """Adapter for ONNX models loaded via ``onnxruntime``.

    Wraps :class:`onnxruntime.InferenceSession` and translates a
    :class:`pandas.DataFrame` into the dict/array format ONNX expects.
    """

    def __init__(self, model_path: str | Path) -> None:
        self._model_path = Path(model_path)
        self._session = ort.InferenceSession(str(self._model_path))
        self._input_meta = self._session.get_inputs()
        self._output_meta = self._session.get_outputs()

    @property
    def feature_names_in_(self) -> list[str] | None:
        """Derive feature names from the ONNX input tensor metadata."""
        if len(self._input_meta) == 1:
            shape = self._input_meta[0].shape
            # If the second dimension is known, we cannot derive names —
            # return None so schema validation is skipped.
            return None
        # Multiple named inputs → treat input names as feature names.
        return [inp.name for inp in self._input_meta]

    def _prepare_input(self, X: pd.DataFrame) -> dict[str, np.ndarray]:
        """Convert a DataFrame to the ONNX input dict."""
        if len(self._input_meta) == 1:
            input_name = self._input_meta[0].name
            return {input_name: X.values.astype(np.float32)}
        # Multiple inputs: map each column → its own input tensor.
        return {
            inp.name: X[inp.name].values.astype(np.float32).reshape(-1, 1)
            for inp in self._input_meta
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        feed = self._prepare_input(X)
        output_name = self._output_meta[0].name
        result = self._session.run([output_name], feed)[0]
        return np.asarray(result).flatten()

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray | None:
        if len(self._output_meta) < 2:
            return None
        feed = self._prepare_input(X)
        proba_name = self._output_meta[1].name
        result = self._session.run([proba_name], feed)[0]
        return np.asarray(result)

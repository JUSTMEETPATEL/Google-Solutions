"""Tests for the faircheck.ingestion module (Phase 2)."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from faircheck.ingestion.datasets import DatasetChunker
from faircheck.ingestion.models import ScikitLearnAdapter, ONNXAdapter
from faircheck.ingestion.pipeline import IngestionPipeline


# ---------------------------------------------------------------
# 1. Protected attribute heuristic detection
# ---------------------------------------------------------------


def test_detect_protected_attributes(tmp_path: Path) -> None:
    """DatasetChunker correctly flags protected columns with confidence >= 0.8."""
    csv_file = tmp_path / "data.csv"
    # "gender" matches regex (+0.5) and has 2 unique string values (+0.4) → 0.9
    # "age" matches regex (+0.5) but is numeric with many uniques → 0.5 (below 0.8)
    # "income" has no regex match and is numeric → 0.0
    csv_file.write_text(
        textwrap.dedent("""\
            gender,age,income
            Male,25,50000
            Female,30,60000
            Male,35,70000
            Female,40,80000
        """)
    )

    chunker = DatasetChunker(csv_file, chunksize=100)
    chunks = list(chunker.iter_chunks())

    assert len(chunks) == 1
    assert "gender" in chunker.detected_protected_attributes
    assert chunker.detected_protected_attributes["gender"] >= 0.8
    # "age" is numeric with 4 uniques → only regex match (0.5) → not detected
    assert "age" not in chunker.detected_protected_attributes
    assert "income" not in chunker.detected_protected_attributes


# ---------------------------------------------------------------
# 2. NaN validation – strict failure
# ---------------------------------------------------------------


def test_chunker_raises_on_nan(tmp_path: Path) -> None:
    """DatasetChunker raises ValueError when NaNs are present."""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        textwrap.dedent("""\
            a,b
            1,2
            3,
            5,6
        """)
    )

    chunker = DatasetChunker(csv_file, chunksize=100)
    with pytest.raises(ValueError, match="Data contains NaN"):
        list(chunker.iter_chunks())


# ---------------------------------------------------------------
# 3. Schema mismatch via IngestionPipeline
# ---------------------------------------------------------------


def test_pipeline_schema_mismatch(tmp_path: Path) -> None:
    """IngestionPipeline raises ValueError on feature mismatch."""
    # Create a CSV that does NOT have "zipcode".
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        textwrap.dedent("""\
            age,income
            25,50000
            30,60000
        """)
    )

    # Create a fake sklearn model that expects ["age", "income", "zipcode"].
    mock_model = MagicMock()
    mock_model.feature_names_in_ = np.array(["age", "income", "zipcode"])
    mock_model.predict.return_value = np.array([0, 1])

    pipeline = IngestionPipeline()

    with patch("faircheck.ingestion.pipeline.ScikitLearnAdapter") as MockAdapter:
        adapter_instance = MockAdapter.return_value
        adapter_instance.feature_names_in_ = ["age", "income", "zipcode"]

        with pytest.raises(ValueError, match="Schema mismatch"):
            pipeline.load(
                model_path=tmp_path / "model.pkl",
                data_path=csv_file,
            )


# ---------------------------------------------------------------
# 4. ScikitLearnAdapter via patched joblib
# ---------------------------------------------------------------


def test_sklearn_adapter_predict(tmp_path: Path) -> None:
    """ScikitLearnAdapter correctly delegates predict to the loaded model."""
    fake_model = MagicMock()
    fake_model.feature_names_in_ = np.array(["a", "b"])
    fake_model.predict.return_value = np.array([0, 1, 0])
    fake_model.predict_proba.return_value = np.array(
        [[0.9, 0.1], [0.2, 0.8], [0.7, 0.3]]
    )

    model_file = tmp_path / "model.pkl"
    model_file.touch()

    with patch("faircheck.ingestion.models.joblib.load", return_value=fake_model):
        adapter = ScikitLearnAdapter(model_file)

    assert adapter.feature_names_in_ == ["a", "b"]

    X = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    preds = adapter.predict(X)
    np.testing.assert_array_equal(preds, [0, 1, 0])

    probas = adapter.predict_proba(X)
    assert probas is not None
    assert probas.shape == (3, 2)


# ---------------------------------------------------------------
# 5. ONNXAdapter via mocked InferenceSession
# ---------------------------------------------------------------


def test_onnx_adapter_predict(tmp_path: Path) -> None:
    """ONNXAdapter correctly translates DataFrame to ONNX input format."""
    mock_input = MagicMock()
    mock_input.name = "input"
    mock_input.shape = [None, 2]

    mock_output_label = MagicMock()
    mock_output_label.name = "label"

    mock_output_proba = MagicMock()
    mock_output_proba.name = "probabilities"

    mock_session = MagicMock()
    mock_session.get_inputs.return_value = [mock_input]
    mock_session.get_outputs.return_value = [mock_output_label, mock_output_proba]
    mock_session.run.side_effect = lambda names, feed: [
        np.array([0, 1]) if names == ["label"] else np.array([[0.9, 0.1], [0.3, 0.7]])
    ]

    model_file = tmp_path / "model.onnx"
    model_file.touch()

    with patch(
        "faircheck.ingestion.models.ort.InferenceSession",
        return_value=mock_session,
    ):
        adapter = ONNXAdapter(model_file)

    # Single-tensor input → feature_names_in_ is None (cannot derive names).
    assert adapter.feature_names_in_ is None

    X = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
    preds = adapter.predict(X)
    np.testing.assert_array_equal(preds, [0, 1])

    probas = adapter.predict_proba(X)
    assert probas is not None
    assert probas.shape == (2, 2)

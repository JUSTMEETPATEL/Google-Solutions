# Phase 2 Research: Model & Dataset Ingestion Pipeline

## Domain Focus & Goal
- **Domain:** Data loading and type inference layer
- **Goal:** Safely load datasets (CSV, JSON, Parquet) handling massive chunks to avoid OOM, load multiple model formats (pkl, joblib, onnx), map them to an agnostic `predict`/`predict_proba` interface, automatically infer protected attributes using heuristics, and hard-crash on NaN values or column mismatches. 

## Architectural Approaches

### 1. Unified Dataset Chunking Model
Since Phase 2 CONTEXT locks in memory safety parsing via chunking:
- **CSV:** `pandas.read_csv(filepath, chunksize=N)`
- **JSON:** `pandas.read_json(filepath, lines=True, chunksize=N)`
- **Parquet:** `pyarrow.parquet.ParquetFile(filepath).iter_batches(batch_size=N)`
We must ensure that the dataset class encapsulates this logic, exposing an iterable `__iter__` or `iter_chunks` generator so the fairness algorithms can evaluate iteratively.

### 2. The Model Interface (`ModelAdapter` base class)
Create an abstract base class `ModelAdapter` with concrete implementations:
- `ScikitLearnAdapter` (Wraps `.pkl`, `.joblib`)
- `ONNXAdapter` (Wraps `.onnx` via `onnxruntime.InferenceSession`)
They must expose standard methods: `predict(X)`, `predict_proba(X)`, and a property `feature_names_in_` that allows schema verification.

### 3. Protected Attribute Heuristics
Heuristics to compute confidence scores (return 0.0 to 1.0):
- **Base Regex Match:** `(?i)(gender|sex|race|ethnicity|age|religion|disability)` -> adds 0.5 to confidence.
- **Uniqueness Check:** If the column dtype is string/categorical and unique values are between 2-10 -> adds 0.4 to confidence.
- Total > 0.8 is treated as automatically detected.

### 4. Validation Architecture (Nyquist Framework)
- Dimension 8 requires validation. We will need a `VALIDATION.md` to define robust tests:
  - Generate fake large CSV/Parquet data without triggering OOM.
  - Test NaNs loading to ensure `ValueError` occurs.
  - Test scikit-learn vs ONNX adapter identical outputs.

## Required Dependencies
The following PyPI packages must be added via `uv add` during the implementation:
- `pyarrow` (Parquet and fast I/O)
- `joblib` (Scikit-learn model loading)
- `onnxruntime` (ONNX mode evaluation)

## Dependencies & Risks
- **Risk:** Type inference on first chunk vs global inference. `pandas` infers types chunk-by-chunk. Mixed types across chunks could crash.
- **Mitigation:** The ingestion layer must force the type detection from the first chunk to apply strictly via `dtype=` overriding on subsequent chunks.

## RESEARCH COMPLETE

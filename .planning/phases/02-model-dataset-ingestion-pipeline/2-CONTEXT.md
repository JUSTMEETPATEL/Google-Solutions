# Phase 2 Context: Model & Dataset Ingestion Pipeline

**Created:** 2026-04-10

## Decisions
- **Model Interface:** Scikit-learn adapter style. Wrap ONNX sessions in a class with `predict()` and `predict_proba()` methods to mimic scikit-learn models perfectly.
- **Data Memory Representation:** Pandas DataFrame. Unifies CSV, JSON, and Parquet datasets into an internal, canonical structure.
- **Protected Attribute Auto-Detection:** Heuristics and Uniqueness checks. Using regex matching combined with string cardinality limits (e.g., 2-5 unique string values) to produce the confidence score natively.
- **Override Mechanics:** Override keywords. The `load_dataset` function directly accepts optional dictionaries like `protected_attributes={...}` and `type_overrides={...}`.
- **Missing Data (NaNs):** Strict validation (fail loudly). Instantly block ingestion on encountering NaNs in the data, enforcing the data science team explicitly cleans data before loading into FairCheck.
- **Large Dataset Handling:** Chunking / Lazy loading. Implement chunked loading via `pandas` and `pyarrow` to avoid extreme memory spikes for multi-gigabyte data files, streaming the inference.
- **Model Schema Validation:** Strict validation. Eagerly align and cross-check the dataset columns with the model's `feature_names_in_` (or the equivalent ONNX map) to fail immediately on mismatches.

## Specifics
- Because dataset chunking is the chosen ingestion strategy, the Python inference adapter explicitly guarantees predicting on small batches, iterating iteratively prior to returning the full array required eventually by AIF360/Fairlearn downstream.

## Canonical Refs
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`

## Deferred Ideas
- None

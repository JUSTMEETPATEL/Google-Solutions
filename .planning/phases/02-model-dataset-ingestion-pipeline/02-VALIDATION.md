# Phase 02 Nyquist Validation Strategy

**Generated:** 2026-04-10

## Validation Architecture

To achieve absolute verification for this phase, we must test both positive evaluation flows and the strict failure constraints requested (NaN failures, shape mismatches, memory overhead limits).

### Dimension 1: Feature Completeness (Positive Path)
- **Scikit-learn Loader:** Successfully loads `.pkl` and `.joblib` models and predicts on a matching `pandas` chunk.
- **ONNX Loader:** Successfully loads `.onnx` models and predicts on a matching `pandas` chunk correctly tracking the identical outputs as scikit-learn.
- **Dataset Loaders:** Generates an internal chunked representation for CSV, Parquet, and JSON.
- **Heuristics:** Successfully assigns `confidence >= 0.8` to columns named `gender`, `race_binary`, or `Age_Bracket`. 

### Dimension 2: Edge Cases (Negative Path)
- **NaN Rejection:** If a CSV chunk contains `NaN` or `None`, the loader MUST raise a `RuntimeError` or `ValueError` with a loud logging block.
- **Schema Validation Reject:** If the dataset features `['age', 'income']` and model expects `['age', 'income', 'zipcode']`, attempting to bind them must raise an exception.

### Dimension 3: Boundary Conditions (Performance)
- **Large Parquet Simulation:** Feed a dataset mocked to have 5 million rows into the pipeline, proving that peak memory never exceeds >250MB because chunk sizes limit memory footprint.

### Dimension 4: State Mutations
- Validating the manual overrides: `load_dataset(filepath, type_overrides={"age": "categorical"})` forces the internally stored dtype map for "age" to be strings/objects rather than int64.

### Dimension 8: Unverifiable Risk Mitigation
- Ensure CI dependencies (onnxruntime, pyarrow) don't bloat the package irreparably. 

## Automated Test Mapping

Tests will go in `tests/test_ingestion.py` and `tests/test_model_adapters.py`.

*Note: For the testing to pass the verifier's strict grep demands, `pytest` must report all corresponding test cases passing.*

---
wave: 1
depends_on: "01"
files_modified:
  - "pyproject.toml"
  - "src/faircheck/ingestion/__init__.py"
  - "src/faircheck/ingestion/models.py"
  - "src/faircheck/ingestion/datasets.py"
  - "src/faircheck/ingestion/pipeline.py"
  - "tests/test_ingestion.py"
autonomous: true
---

# Phase 02: Model & Dataset Ingestion Pipeline

## requirements
ING-01, ING-02, ING-03, ING-04, ING-05, ING-06, ING-07, ING-08, ING-09

## must_haves
1. Can load `.pkl`, `.joblib`, and `.onnx` models correctly with a uniform `predict()` and `predict_proba()` adapter interface.
2. Can load CSV, Parquet, and JSON datasets incrementally via chunks leveraging `pandas` and `pyarrow`.
3. Type inference identifies feature data types.
4. Heuristic auto-detection accurately flags protected attributes (`confidence >= 0.8`) utilizing uniqueness/regex combinations.
5. Emits strict failure blocks on `NaNs` and on model schema mismatches.

## tasks

```xml
<task>
  <read_first>
    <file>pyproject.toml</file>
  </read_first>
  <action>
    Modify `pyproject.toml` to include the required model and data loading dependencies.
    Add `pyarrow`, `joblib`, and `onnxruntime` to the standard dependencies block. 
    Then, add `pytest-mock` to the dependency-groups (dev) block.
    After modifying, run `uv sync` to ensure the environment is updated.
  </action>
  <acceptance_criteria>
    - `pyproject.toml` contains `pyarrow`
    - `pyproject.toml` contains `joblib`
    - `pyproject.toml` contains `onnxruntime`
    - `pyproject.toml` contains `pytest-mock` under dev dependency groups
    - `uv sync` command succeeds
  </acceptance_criteria>
</task>
```

```xml
<task>
  <read_first>
    <file>src/faircheck/algorithms/base.py</file>
  </read_first>
  <action>
    Create the directory `src/faircheck/ingestion` and an empty `__init__.py` file.
    Create `src/faircheck/ingestion/models.py`.
    Implement the `ModelAdapter` abstract base class with methods `predict(X)`, `predict_proba(X)`, and a property `feature_names_in_`.
    Implement `ScikitLearnAdapter` which takes a `model_path` (str), loads it via `joblib.load(model_path)` (handles .pkl and .joblib), and delegates predict/proba appropriately.
    Implement `ONNXAdapter` which uses `onnxruntime.InferenceSession`. The `feature_names_in_` relies on `session.get_inputs()[0].name` (for simple single tensor inputs) and maps the input dictionaries appropriately for `predict(X)` using pandas to dictionary conversions.
  </action>
  <acceptance_criteria>
    - `src/faircheck/ingestion/models.py` contains `class ModelAdapter(ABC)`
    - `src/faircheck/ingestion/models.py` contains `import joblib` and `import onnxruntime`
    - `src/faircheck/ingestion/models.py` contains `ScikitLearnAdapter` and `ONNXAdapter`
  </acceptance_criteria>
</task>
```

```xml
<task>
  <read_first>
    <file>src/faircheck/ingestion/models.py</file>
  </read_first>
  <action>
    Create `src/faircheck/ingestion/datasets.py`.
    Implement `DatasetChunker` class to handle large files.
    The chunker initializes with `filepath` (CSV, Parquet, JSON), `chunksize` (int, default 100000), `protected_attributes_overrides` (dict), and `type_overrides` (dict).
    
    Implement a method `_detect_protected_attributes(df)`:
    Iterate dataframe columns. If regex matches `(?i)(gender|sex|race|ethnicity|age|religion|disability)`, add 0.5. 
    If column type is categorical/string/object and counts `2 &lt;= df[col].nunique() &lt;= 10`, add 0.4.
    If total confidence &gt;= 0.8, log and mark as protected.
    
    Implement a method `iter_chunks()` that yields a DataFrame slice.
    For `.csv`: use `pd.read_csv(chunksize=chunksize)`. 
    For `.json`: use `pd.read_json(lines=True, chunksize=chunksize)`.
    For `.parquet`: use `pyarrow.parquet.ParquetFile(filepath).iter_batches()` and yield `batch.to_pandas()`.
    Before yielding any chunk, run it through `_detect_protected_attributes()` and strictly drop or raise an Error on NaNs (using `if df.isnull().values.any(): raise ValueError("Data contains NaNs")`). Apply configured overrides.
  </action>
  <acceptance_criteria>
    - `src/faircheck/ingestion/datasets.py` contains `DatasetChunker`
    - `src/faircheck/ingestion/datasets.py` contains logic to raise ValueError on NaNs
    - `src/faircheck/ingestion/datasets.py` contains `(?i)(gender|sex|race|ethnicity|age|religion|disability)`
    - the class exposes `iter_chunks()` method that supports csv, json, and parquet.
  </acceptance_criteria>
</task>
```

```xml
<task>
  <read_first>
    <file>src/faircheck/ingestion/datasets.py</file>
  </read_first>
  <action>
    Create `src/faircheck/ingestion/pipeline.py`.
    Implement an `IngestionPipeline` facade or manager.
    Method `load(model_path, data_path, type_overrides=None, protected_overrides=None)`.
    Instantiates the correct adapter (ONNX or Scikit) depending on the `model_path` extension. 
    Instantiates `DatasetChunker(data_path, ...)`
    
    Implement schema validation: Peek at the first chunk from `DatasetChunker.iter_chunks()`. 
    Compare chunk's column names against `ModelAdapter.feature_names_in_` if the model defines them. 
    If there is a mismatch, raise `ValueError("Schema mismatch: ...")`.
  </action>
  <acceptance_criteria>
    - `src/faircheck/ingestion/pipeline.py` contains `IngestionPipeline` class
    - The `IngestionPipeline.load` definition expects 4 arguments correctly
    - Code raises `ValueError` if features misalign schema
  </acceptance_criteria>
</task>
```

```xml
<task>
  <read_first>
    <file>src/faircheck/ingestion/pipeline.py</file>
  </read_first>
  <action>
    Create `tests/test_ingestion.py`.
    Write 5 full tests using Pytest and mocker to achieve 100% component coverage representing the validation structure.
    1. Test `DatasetChunker` effectively detects protected columns with the heuristic scoring on a toy DataFrame. 
    2. Test `DatasetChunker` iter_chunks successfully yields chunks and immediately crashes via ValueError on encountering a NaN input chunk.
    3. Test `IngestionPipeline` successfully binds a fake ScikitLearn model to data inputs, validating that Schema Mismatch generates an exception.
    4. Test `ScikitLearnAdapter` returns correct paths manually via patched instances.
    5. Test ONNX formatting adapter mapping via `MagicMock()` on `onnxruntime.InferenceSession`.
  </action>
  <acceptance_criteria>
    - `tests/test_ingestion.py` exists and contains at least 5 functions starting with `test_`
    - `uv run pytest tests/test_ingestion.py` output states 100% tests pass (all green)
  </acceptance_criteria>
</task>
```

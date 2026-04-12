"""End-to-end integration tests — full pipeline from analysis to report (INT-05)."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from faircheck.analysis.engine import BiasAnalyzer
from faircheck.mitigation import MitigationPipeline
from faircheck.reports import ReportBuilder, ReportEngine
from faircheck.reports.data import ReportData
from faircheck.reports.regulation import RegulationMapper
from faircheck.api.lifecycle import (
    PORT_FILE,
    PID_FILE,
    cleanup_files,
    read_port_file,
    write_port_file,
)


@pytest.fixture
def synthetic_pipeline():
    """Create synthetic data + trained model for full pipeline test."""
    rng = np.random.default_rng(42)
    n = 300

    X = rng.standard_normal((n, 5))
    gender = pd.Series(["male"] * 150 + ["female"] * 150)
    y = np.concatenate([
        rng.choice([0, 1], p=[0.3, 0.7], size=150),
        rng.choice([0, 1], p=[0.5, 0.5], size=150),
    ])

    # Train model
    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(X[:200], y[:200])
    y_pred = model.predict(X[200:])

    return {
        "X_train": X[:200],
        "y_train": y[:200],
        "X_test": X[200:],
        "y_test": y[200:],
        "y_pred": y_pred,
        "gender_train": gender[:200],
        "gender_test": gender[200:],
        "model": model,
    }


class TestFullPipeline:
    """INT-05: End-to-end flow — analysis → mitigation → report."""

    def test_analysis_to_report(self, synthetic_pipeline, tmp_path):
        """Full pipeline: analyze → generate report → verify PDF exists."""
        p = synthetic_pipeline

        # Step 1: Run bias analysis
        analyzer = BiasAnalyzer()
        result = analyzer.analyze(
            y_true=p["y_test"],
            y_pred=p["y_pred"],
            sensitive_features={"gender": p["gender_test"]},
        )

        assert result.overall_risk_level in ("low", "medium", "high")
        analysis_dict = result.to_dict()
        assert "results" in analysis_dict
        assert "gender" in analysis_dict["results"]

        # Step 2: Build report
        report_dict = {
            "model_name": "IntegrationTestModel",
            "model_version": "1.0",
            "session_id": "e2e-test-001",
            "analysis_results": analysis_dict,
        }
        builder = ReportBuilder()
        paths = builder.build(
            report_dict,
            formats=["pdf", "md"],
            output_dir=tmp_path,
        )

        assert "pdf" in paths
        assert "md" in paths
        assert paths["pdf"].exists()
        assert paths["md"].exists()
        assert paths["pdf"].stat().st_size > 0
        assert paths["md"].stat().st_size > 0

        # Verify markdown contains analysis data
        md_content = paths["md"].read_text()
        assert "IntegrationTestModel" in md_content
        assert "Gender" in md_content or "gender" in md_content.lower()

    def test_analysis_mitigation_report(self, synthetic_pipeline, tmp_path):
        """Full pipeline with mitigation: analyze → mitigate → analyze → report."""
        p = synthetic_pipeline

        # Step 1: Run initial bias analysis
        analyzer = BiasAnalyzer()
        before = analyzer.analyze(
            y_true=p["y_test"],
            y_pred=p["y_pred"],
            sensitive_features={"gender": p["gender_test"]},
        )

        # Step 2: Apply mitigation
        pipeline = MitigationPipeline()
        mitigation_result = pipeline.run(
            algorithm="reweighing",
            X_train=p["X_train"],
            y_train=p["y_train"],
            X_test=p["X_test"],
            y_test=p["y_test"],
            sensitive_features={
                "gender": (p["gender_train"], p["gender_test"]),
            },
        )

        assert mitigation_result.success is True
        assert mitigation_result.before_metrics != {}
        assert mitigation_result.after_metrics != {}

        # Step 3: Generate report with after-mitigation data
        report_dict = {
            "model_name": "MitigatedModel",
            "session_id": "e2e-mitigated-001",
            "analysis_results": mitigation_result.after_metrics,
            "mitigation": {
                "algorithm": "reweighing",
                "category": "pre-processing",
            },
        }
        builder = ReportBuilder()
        paths = builder.build(
            report_dict,
            formats=["pdf"],
            output_dir=tmp_path,
        )

        assert paths["pdf"].exists()
        assert paths["pdf"].stat().st_size > 0

    def test_report_with_eu_ai_act(self, synthetic_pipeline, tmp_path):
        """Full pipeline with EU AI Act regulation templates."""
        p = synthetic_pipeline

        analyzer = BiasAnalyzer()
        result = analyzer.analyze(
            y_true=p["y_test"],
            y_pred=p["y_pred"],
            sensitive_features={"gender": p["gender_test"]},
        )

        report_dict = {
            "model_name": "RegulatedModel",
            "session_id": "e2e-regulated-001",
            "intended_use": "Hiring screening",
            "training_data_description": "10k employee records",
            "analysis_results": result.to_dict(),
        }
        builder = ReportBuilder()
        paths = builder.build(
            report_dict,
            formats=["md"],
            output_dir=tmp_path,
            regulation="eu_ai_act",
        )

        md_content = paths["md"].read_text()
        assert "Article 9" in md_content
        assert "Article 14" in md_content
        assert "DISCLAIMER" in md_content

    def test_report_with_oversight(self, synthetic_pipeline, tmp_path):
        """Full pipeline with human oversight record."""
        p = synthetic_pipeline

        analyzer = BiasAnalyzer()
        result = analyzer.analyze(
            y_true=p["y_test"],
            y_pred=p["y_pred"],
            sensitive_features={"gender": p["gender_test"]},
        )

        report_dict = {
            "model_name": "OversightModel",
            "session_id": "e2e-oversight-001",
            "analysis_results": result.to_dict(),
            "oversight": {
                "reviewer": "Dr. Alice Johnson",
                "date": "2026-04-12",
                "decision": "approved",
                "notes": "All metrics within thresholds.",
            },
        }

        # Verify RegulationMapper handles oversight
        data = ReportData.from_dict(report_dict)
        mapper = RegulationMapper()
        reg_report = mapper.map(data)
        art14 = [m for m in reg_report.article_mappings if m.article == "Article 14"][0]
        assert art14.status == "addressed"
        assert "Dr. Alice Johnson" in art14.evidence


class TestPortIntegration:
    """INT-02: Port file integration."""

    def test_port_roundtrip(self):
        write_port_file(8042)
        assert read_port_file() == 8042
        cleanup_files()
        assert read_port_file() is None


class TestMultiFormatReport:
    """Verify all three report formats in single build call."""

    def test_all_three_formats(self, synthetic_pipeline, tmp_path):
        p = synthetic_pipeline

        analyzer = BiasAnalyzer()
        result = analyzer.analyze(
            y_true=p["y_test"],
            y_pred=p["y_pred"],
            sensitive_features={"gender": p["gender_test"]},
        )

        report_dict = {
            "model_name": "MultiFormatModel",
            "analysis_results": result.to_dict(),
        }
        builder = ReportBuilder()
        paths = builder.build(
            report_dict,
            formats=["pdf", "md", "docx"],
            output_dir=tmp_path,
        )

        assert len(paths) == 3
        for fmt in ("pdf", "md", "docx"):
            assert fmt in paths
            assert paths[fmt].exists()
            assert paths[fmt].stat().st_size > 0

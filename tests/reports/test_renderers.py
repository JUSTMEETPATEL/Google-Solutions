"""Tests for report renderers."""

from pathlib import Path

import pytest

from faircheck.reports.charts import generate_charts
from faircheck.reports.data import ReportData
from faircheck.reports.engine import ReportEngine
from faircheck.reports.renderers import ReportBuilder


@pytest.fixture
def sample_report_dict():
    """Realistic report data dict for testing."""
    return {
        "model_name": "HiringClassifier",
        "model_version": "1.3",
        "audit_date": "2026-04-11",
        "reviewer": "Dr. Alice Smith",
        "regulation_standard": "EU AI Act",
        "session_id": "test-session-001",
        "training_data_description": "50k employee records from 2020-2025.",
        "intended_use": "Screening applicants for software engineering roles.",
        "known_limitations": "Limited representation of non-binary gender identities.",
        "analysis_results": {
            "overall_risk_level": "medium",
            "results": {
                "gender": {
                    "metrics": {
                        "demographic_parity_difference": {
                            "name": "demographic_parity_difference",
                            "value": 0.08,
                            "threshold": 0.10,
                            "status": "warning",
                            "details": {"by_group": {"male": 0.6, "female": 0.52}},
                            "warning_message": None,
                        },
                        "equalized_odds_difference": {
                            "name": "equalized_odds_difference",
                            "value": 0.12,
                            "threshold": 0.10,
                            "status": "fail",
                            "details": {},
                            "warning_message": None,
                        },
                        "disparate_impact_ratio": {
                            "name": "disparate_impact_ratio",
                            "value": 0.87,
                            "threshold": 0.80,
                            "status": "pass",
                            "details": {},
                            "warning_message": None,
                        },
                    },
                    "performance_breakdown": {
                        "male": {"accuracy": 0.91, "precision": 0.88, "recall": 0.90, "f1": 0.89},
                        "female": {"accuracy": 0.86, "precision": 0.82, "recall": 0.84, "f1": 0.83},
                    },
                },
            },
            "scan_metadata": {
                "timestamp": "2026-04-11T12:00:00Z",
                "sample_size": 5000,
                "metrics_computed": 5,
            },
        },
    }


class TestReportEngine:
    def test_render_html(self, sample_report_dict):
        engine = ReportEngine()
        data = ReportData.from_dict(sample_report_dict)
        html = engine.render_html(data)
        assert "<!DOCTYPE html>" in html
        assert "HiringClassifier" in html
        assert "Dr. Alice Smith" in html

    def test_render_markdown(self, sample_report_dict):
        engine = ReportEngine()
        data = ReportData.from_dict(sample_report_dict)
        md = engine.render_markdown(data)
        assert "# AI Bias Audit Report" in md
        assert "HiringClassifier" in md

    def test_html_contains_metrics_table(self, sample_report_dict):
        engine = ReportEngine()
        data = ReportData.from_dict(sample_report_dict)
        html = engine.render_html(data)
        assert "Demographic Parity Difference" in html
        assert "FAIL" in html or "fail" in html.lower()
        assert "WARNING" in html or "warning" in html.lower()

    def test_html_placeholder_mitigation(self, sample_report_dict):
        engine = ReportEngine()
        data = ReportData.from_dict(sample_report_dict)
        html = engine.render_html(data)
        assert "No mitigation has been applied" in html

    def test_html_placeholder_oversight(self, sample_report_dict):
        engine = ReportEngine()
        data = ReportData.from_dict(sample_report_dict)
        html = engine.render_html(data)
        assert "No human oversight decision" in html


class TestChartGeneration:
    def test_generate_charts(self, sample_report_dict):
        charts = generate_charts(sample_report_dict["analysis_results"])
        assert isinstance(charts, dict)
        assert len(charts) > 0
        for name, b64 in charts.items():
            assert isinstance(b64, str)
            assert len(b64) > 100  # Not empty

    def test_chart_names(self, sample_report_dict):
        charts = generate_charts(sample_report_dict["analysis_results"])
        assert "performance_gender" in charts
        assert "metrics_gender" in charts


class TestReportBuilder:
    def test_build_markdown(self, sample_report_dict, tmp_path):
        builder = ReportBuilder()
        paths = builder.build(
            sample_report_dict, formats=["md"], output_dir=tmp_path
        )
        assert "md" in paths
        assert paths["md"].exists()
        content = paths["md"].read_text()
        assert "HiringClassifier" in content

    def test_build_docx(self, sample_report_dict, tmp_path):
        builder = ReportBuilder()
        paths = builder.build(
            sample_report_dict, formats=["docx"], output_dir=tmp_path
        )
        assert "docx" in paths
        assert paths["docx"].exists()
        assert paths["docx"].stat().st_size > 0

    def test_build_pdf(self, sample_report_dict, tmp_path):
        builder = ReportBuilder()
        try:
            paths = builder.build(
                sample_report_dict, formats=["pdf"], output_dir=tmp_path
            )
            assert "pdf" in paths
            assert paths["pdf"].exists()
        except OSError:
            # WeasyPrint may fail in CI if system fonts/libs are missing
            pytest.skip("WeasyPrint system dependencies not available")

    def test_build_multiple_formats(self, sample_report_dict, tmp_path):
        builder = ReportBuilder()
        try:
            paths = builder.build(
                sample_report_dict, formats=["md", "docx"], output_dir=tmp_path
            )
            assert "md" in paths
            assert "docx" in paths
        except OSError:
            pytest.skip("System dependencies not available")

    def test_empty_analysis(self, tmp_path):
        builder = ReportBuilder()
        paths = builder.build({}, formats=["md"], output_dir=tmp_path)
        assert "md" in paths
        content = paths["md"].read_text()
        assert "Unknown Model" in content

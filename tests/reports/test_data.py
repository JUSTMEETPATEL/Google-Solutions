"""Tests for ReportData contract."""

import pytest

from faircheck.reports.data import ReportData


class TestReportData:
    def test_from_dict_defaults(self):
        rd = ReportData.from_dict({})
        assert rd.model_name == "Unknown Model"
        assert rd.model_version == "1.0"
        assert rd.reviewer == ""
        assert rd.regulation_standard == "EU AI Act"
        assert rd.mitigation is None
        assert rd.oversight is None
        assert rd.analysis_results == {}

    def test_from_dict_with_values(self):
        rd = ReportData.from_dict({
            "model_name": "TestModel",
            "model_version": "2.1",
            "reviewer": "Alice",
            "regulation_standard": "Custom",
            "session_id": "abc-123",
        })
        assert rd.model_name == "TestModel"
        assert rd.model_version == "2.1"
        assert rd.reviewer == "Alice"
        assert rd.session_id == "abc-123"

    def test_from_dict_with_analysis_results(self):
        results = {
            "overall_risk_level": "high",
            "results": {
                "gender": {
                    "metrics": {
                        "demographic_parity_difference": {
                            "value": 0.15,
                            "threshold": 0.10,
                            "status": "fail",
                        }
                    },
                    "performance_breakdown": {
                        "male": {"accuracy": 0.9, "precision": 0.85, "recall": 0.88, "f1": 0.86},
                        "female": {"accuracy": 0.85, "precision": 0.80, "recall": 0.82, "f1": 0.81},
                    },
                }
            },
        }
        rd = ReportData.from_dict({"analysis_results": results})
        assert rd.analysis_results["overall_risk_level"] == "high"
        assert "gender" in rd.analysis_results["results"]

    def test_mitigation_placeholder(self):
        rd = ReportData.from_dict({})
        assert rd.mitigation is None  # D-06: placeholder shown

    def test_oversight_placeholder(self):
        rd = ReportData.from_dict({})
        assert rd.oversight is None  # D-06: placeholder shown

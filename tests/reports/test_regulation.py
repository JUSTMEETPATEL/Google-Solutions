"""Tests for EU AI Act regulation templates and mapper."""

import pytest

from faircheck.reports.data import ReportData
from faircheck.reports.engine import ReportEngine
from faircheck.reports.regulation import (
    ArticleMapping,
    RegulationMapper,
    RegulationReport,
)


@pytest.fixture
def sample_data_passing():
    """Report data where all metrics pass."""
    return ReportData.from_dict({
        "model_name": "HiringModel",
        "model_version": "2.0",
        "session_id": "sess-001",
        "training_data_description": "10k records from 2020-2024",
        "intended_use": "Resume screening for software engineering roles.",
        "known_limitations": "Limited non-binary representation.",
        "analysis_results": {
            "overall_risk_level": "low",
            "results": {
                "gender": {
                    "metrics": {
                        "demographic_parity_difference": {
                            "value": 0.03,
                            "threshold": 0.1,
                            "status": "pass",
                        },
                        "equalized_odds_difference": {
                            "value": 0.05,
                            "threshold": 0.1,
                            "status": "pass",
                        },
                    },
                    "performance_breakdown": {
                        "male": {"accuracy": 0.85, "precision": 0.82, "recall": 0.88, "f1": 0.85},
                        "female": {"accuracy": 0.83, "precision": 0.80, "recall": 0.86, "f1": 0.83},
                    },
                },
            },
        },
    })


@pytest.fixture
def sample_data_failing():
    """Report data where some metrics fail."""
    return ReportData.from_dict({
        "model_name": "LendingModel",
        "analysis_results": {
            "overall_risk_level": "high",
            "results": {
                "race": {
                    "metrics": {
                        "demographic_parity_difference": {
                            "value": 0.25,
                            "threshold": 0.1,
                            "status": "fail",
                        },
                        "disparate_impact_ratio": {
                            "value": 0.65,
                            "threshold": 0.8,
                            "status": "warning",
                        },
                    },
                },
            },
        },
    })


@pytest.fixture
def sample_data_with_oversight():
    """Report data with oversight record."""
    data = ReportData.from_dict({
        "model_name": "TestModel",
        "analysis_results": {
            "overall_risk_level": "low",
            "results": {
                "gender": {
                    "metrics": {
                        "dpd": {"value": 0.02, "threshold": 0.1, "status": "pass"},
                    },
                },
            },
        },
        "oversight": {
            "reviewer": "Dr. Jane Smith",
            "date": "2026-04-11",
            "decision": "approved",
            "notes": "All metrics within thresholds.",
        },
    })
    return data


# ─── RegulationMapper Tests ────────────────────────────────


class TestRegulationMapper:
    def test_map_returns_regulation_report(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        assert isinstance(result, RegulationReport)
        assert result.regulation == "eu_ai_act"

    def test_five_article_mappings(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        assert len(result.article_mappings) == 5
        articles = [m.article for m in result.article_mappings]
        assert "Article 9" in articles
        assert "Article 10" in articles
        assert "Article 13" in articles
        assert "Article 14" in articles
        assert "Article 17" in articles

    def test_risk_classification_low(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        assert result.risk_classification == "low"

    def test_risk_classification_high(self, sample_data_failing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_failing)
        assert result.risk_classification == "high"

    def test_risk_classification_medium(self):
        data = ReportData.from_dict({
            "analysis_results": {
                "results": {
                    "age": {
                        "metrics": {
                            "dpd": {"value": 0.08, "threshold": 0.1, "status": "warning"},
                        },
                    },
                },
            },
        })
        mapper = RegulationMapper()
        result = mapper.map(data)
        assert result.risk_classification == "medium"

    def test_disclaimer_present(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        assert result.disclaimer
        assert "DISCLAIMER" in result.disclaimer
        assert "legal certification" in result.disclaimer

    def test_article_14_addressed_with_oversight(self, sample_data_with_oversight):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_with_oversight)
        art14 = [m for m in result.article_mappings if m.article == "Article 14"][0]
        assert art14.status == "addressed"
        assert "Dr. Jane Smith" in art14.evidence

    def test_article_14_not_addressed_without_oversight(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        art14 = [m for m in result.article_mappings if m.article == "Article 14"][0]
        assert art14.status == "not_addressed"

    def test_to_dict(self, sample_data_passing):
        mapper = RegulationMapper()
        result = mapper.map(sample_data_passing)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["regulation"] == "eu_ai_act"
        assert len(d["article_mappings"]) == 5


# ─── Template Rendering Tests ──────────────────────────────


class TestRegulationTemplates:
    def test_eu_ai_act_html_renders(self, sample_data_passing):
        engine = ReportEngine()
        html = engine.render_html(sample_data_passing, regulation="eu_ai_act")
        assert "Article 9" in html
        assert "Article 10" in html
        assert "Article 13" in html
        assert "Article 14" in html
        assert "Article 17" in html
        assert "DISCLAIMER" in html

    def test_eu_ai_act_md_renders(self, sample_data_passing):
        engine = ReportEngine()
        md = engine.render_markdown(sample_data_passing, regulation="eu_ai_act")
        assert "Article 9" in md
        assert "Article 14" in md
        assert "DISCLAIMER" in md

    def test_cross_reference_in_html(self, sample_data_passing):
        engine = ReportEngine()
        html = engine.render_html(sample_data_passing, regulation="eu_ai_act")
        assert "Regulatory Cross-Reference" in html
        assert "Risk Management" in html

    def test_standard_template_still_works(self, sample_data_passing):
        """Non-regulation render should not include regulation sections."""
        engine = ReportEngine()
        html = engine.render_html(sample_data_passing)
        assert "FairCheck AI Bias Audit Report" in html
        # Standard template should NOT have regulation sections
        assert "Regulatory Cross-Reference" not in html

    def test_failing_metrics_show_risks(self, sample_data_failing):
        engine = ReportEngine()
        html = engine.render_html(sample_data_failing, regulation="eu_ai_act")
        assert "Identified Risks" in html
        assert "FAIL" in html

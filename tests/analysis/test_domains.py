"""Tests for domain guidance module."""

from faircheck.analysis.domains import (
    DOMAIN_GUIDANCE,
    get_domain_guidance,
    list_supported_domains,
)


class TestDomainGuidance:
    def test_hiring_guidance(self):
        g = get_domain_guidance("hiring")
        assert g is not None
        assert "demographic_parity_difference" in g["recommended_metrics"]
        assert "disparate_impact_ratio" in g["recommended_metrics"]

    def test_lending_guidance(self):
        g = get_domain_guidance("lending")
        assert g is not None
        assert "equalized_odds_difference" in g["recommended_metrics"]

    def test_healthcare_guidance(self):
        g = get_domain_guidance("healthcare")
        assert g is not None
        assert "calibration_by_group" in g["recommended_metrics"]

    def test_unknown_domain_returns_none(self):
        assert get_domain_guidance("unknown") is None

    def test_none_domain_returns_none(self):
        assert get_domain_guidance(None) is None

    def test_case_insensitive(self):
        assert get_domain_guidance("HIRING") is not None
        assert get_domain_guidance("Lending") is not None

    def test_list_supported(self):
        domains = list_supported_domains()
        assert "hiring" in domains
        assert "lending" in domains
        assert "healthcare" in domains
        assert len(domains) == 3

    def test_guidance_structure(self):
        """All domains have required keys."""
        for domain_name, guidance in DOMAIN_GUIDANCE.items():
            assert "recommended_metrics" in guidance, f"{domain_name} missing recommended_metrics"
            assert "critical_thresholds" in guidance, f"{domain_name} missing critical_thresholds"
            assert "rationale" in guidance, f"{domain_name} missing rationale"
            assert "regulations" in guidance, f"{domain_name} missing regulations"

"""
🔴 RED: Unit tests for Risk Pydantic schemas.

Tests para validar los schemas de Risk (request/response).
"""

from datetime import date, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.features.risk_assessment.schemas.risk import (
    RiskBase,
    RiskCreate,
    RiskResponse,
    RiskSummary,
    RiskUpdate,
)


class TestRiskBase:
    """Tests for RiskBase schema."""

    def test_risk_base_valid_data(self):
        """
        🔴 RED: Test RiskBase with valid data.
        """
        data = {
            "title": "SQL Injection Vulnerability",
            "description": "Critical SQL injection found in login endpoint",
            "severity": "critical",
            "likelihood": "high",
            "impact_score": 9.5,
            "category": "technical",
        }
        risk = RiskBase(**data)
        assert risk.title == "SQL Injection Vulnerability"
        assert risk.severity == "critical"
        assert risk.impact_score == 9.5

    def test_risk_base_title_too_short(self):
        """
        🔴 RED: Test title min_length validation.
        """
        data = {
            "title": "SQL",  # Too short (< 5 chars)
            "description": "Test description",
            "severity": "high",
            "likelihood": "medium",
            "impact_score": 7.0,
            "category": "technical",
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskBase(**data)
        assert "title" in str(exc_info.value)

    def test_risk_base_title_too_long(self):
        """
        🔴 RED: Test title max_length validation.
        """
        data = {
            "title": "A" * 256,  # Too long (> 255 chars)
            "description": "Test description",
            "severity": "medium",
            "likelihood": "low",
            "impact_score": 5.0,
            "category": "operational",
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskBase(**data)
        assert "title" in str(exc_info.value)

    def test_risk_base_impact_score_below_range(self):
        """
        🔴 RED: Test impact_score must be >= 0.0.
        """
        data = {
            "title": "Test Risk",
            "description": "Test description",
            "severity": "low",
            "likelihood": "low",
            "impact_score": -1.0,  # Below range
            "category": "compliance",
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskBase(**data)
        assert "impact_score" in str(exc_info.value)

    def test_risk_base_impact_score_above_range(self):
        """
        🔴 RED: Test impact_score must be <= 10.0.
        """
        data = {
            "title": "Test Risk",
            "description": "Test description",
            "severity": "critical",
            "likelihood": "high",
            "impact_score": 15.0,  # Above range
            "category": "technical",
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskBase(**data)
        assert "impact_score" in str(exc_info.value)


class TestRiskCreate:
    """Tests for RiskCreate schema."""

    def test_risk_create_without_risk_number(self):
        """
        🔴 RED: Test RiskCreate allows creation without risk_number.
        """
        data = {
            "title": "New Risk",
            "description": "Risk without explicit risk_number",
            "severity": "high",
            "likelihood": "medium",
            "impact_score": 7.5,
            "category": "technical",
        }
        risk = RiskCreate(**data)
        assert risk.title == "New Risk"
        assert not hasattr(risk, "risk_number") or risk.risk_number is None

    def test_risk_create_with_optional_fields(self):
        """
        🔴 RED: Test RiskCreate with all optional fields.
        """
        data = {
            "title": "Complete Risk",
            "description": "Risk with all fields",
            "severity": "critical",
            "likelihood": "high",
            "impact_score": 9.0,
            "category": "technical",
            "status": "in_progress",
            "assigned_to": "security@company.com",
            "mitigation_plan": "Apply security patches immediately",
            "deadline": "2026-12-31",
        }
        risk = RiskCreate(**data)
        assert risk.assigned_to == "security@company.com"
        assert risk.mitigation_plan == "Apply security patches immediately"

    def test_risk_create_invalid_email(self):
        """
        🔴 RED: Test assigned_to email validation.
        """
        data = {
            "title": "Test Risk",
            "description": "Test description",
            "severity": "medium",
            "likelihood": "low",
            "impact_score": 5.0,
            "category": "operational",
            "assigned_to": "not-an-email",  # Invalid email
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskCreate(**data)
        assert "assigned_to" in str(exc_info.value)

    def test_risk_create_deadline_in_past(self):
        """
        🔴 RED: Test deadline must be future date.
        """
        data = {
            "title": "Test Risk",
            "description": "Test description",
            "severity": "low",
            "likelihood": "low",
            "impact_score": 2.0,
            "category": "compliance",
            "deadline": "2020-01-01",  # Past date
        }
        with pytest.raises(ValidationError) as exc_info:
            RiskCreate(**data)
        assert "deadline" in str(exc_info.value)


class TestRiskUpdate:
    """Tests for RiskUpdate schema."""

    def test_risk_update_all_fields_optional(self):
        """
        🔴 RED: Test RiskUpdate allows partial updates.
        """
        # Update only title
        update1 = RiskUpdate(title="Updated Title")
        assert update1.title == "Updated Title"
        assert update1.severity is None

        # Update only status
        update2 = RiskUpdate(status="mitigated")
        assert update2.status == "mitigated"
        assert update2.title is None

    def test_risk_update_empty_is_valid(self):
        """
        🔴 RED: Test empty RiskUpdate is valid.
        """
        update = RiskUpdate()
        assert update.title is None
        assert update.severity is None
        assert update.status is None

    def test_risk_update_validates_fields(self):
        """
        🔴 RED: Test RiskUpdate validates field constraints.
        """
        # Invalid impact_score
        with pytest.raises(ValidationError):
            RiskUpdate(impact_score=15.0)

        # Invalid email
        with pytest.raises(ValidationError):
            RiskUpdate(assigned_to="invalid-email")


class TestRiskResponse:
    """Tests for RiskResponse schema."""

    def test_risk_response_includes_all_fields(self):
        """
        🔴 RED: Test RiskResponse includes all fields including DB ones.
        """
        data = {
            "id": str(uuid4()),
            "risk_number": "RISK-2026-001",
            "title": "Test Risk",
            "description": "Test description",
            "severity": "high",
            "likelihood": "medium",
            "impact_score": 7.0,
            "status": "open",
            "category": "technical",
            "assigned_to": None,
            "mitigation_plan": None,
            "deadline": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        risk = RiskResponse(**data)
        assert risk.id is not None
        assert risk.risk_number == "RISK-2026-001"
        assert risk.created_at is not None

    def test_risk_response_from_orm(self):
        """
        🔴 RED: Test RiskResponse works with ORM models (from_attributes).
        """
        # This will be tested with actual Risk model in integration tests
        # Here we just verify the schema allows it
        assert RiskResponse.model_config.get("from_attributes") is True


class TestRiskSummary:
    """Tests for RiskSummary schema."""

    def test_risk_summary_essential_fields_only(self):
        """
        🔴 RED: Test RiskSummary contains only essential fields.
        """
        data = {
            "id": str(uuid4()),
            "risk_number": "RISK-2026-001",
            "title": "Test Risk",
            "severity": "critical",
            "status": "open",
            "calculated_risk_score": 9.5,
        }
        summary = RiskSummary(**data)
        assert summary.risk_number == "RISK-2026-001"
        assert summary.calculated_risk_score == 9.5

        # Should not have description or other verbose fields
        assert not hasattr(summary, "description")
        assert not hasattr(summary, "mitigation_plan")

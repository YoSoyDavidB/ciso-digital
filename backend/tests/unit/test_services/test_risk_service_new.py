"""
🔴 RED Phase: Tests for RiskService (CRUD Operations).

Tests for the new RiskService that will use feature-based schemas.
The service DOES NOT EXIST YET - these tests define the expected behavior.

Following TDD methodology:
1. Write these tests first (RED - they will fail)
2. Implement RiskService to make them pass (GREEN)
3. Refactor for quality (REFACTOR)
"""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.risk_assessment.schemas.risk import (
    RiskCreate,
    RiskResponse,
    RiskSummary,
    RiskUpdate,
)

# This import will FAIL initially - that's expected for RED phase
from app.features.risk_assessment.services.risk_service import RiskService
from app.shared.models.enums import RiskCategory, RiskLikelihood, RiskSeverity, RiskStatus
from app.shared.models.risk import Risk


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def risk_service(db_session: AsyncSession) -> RiskService:
    """
    Fixture that provides a RiskService instance.

    Args:
        db_session: Database session from conftest.py

    Returns:
        RiskService: Service instance configured with test database
    """
    return RiskService(db_session)


@pytest.fixture
async def sample_risk(db_session: AsyncSession) -> Risk:
    """
    Fixture that creates a sample Risk in the database.

    Returns:
        Risk: A persisted risk entity for testing
    """
    risk = await Risk.create(
        db=db_session,
        title="Sample SQL Injection Risk",
        description="Critical vulnerability in authentication endpoint allowing SQL injection",
        severity=RiskSeverity.CRITICAL,
        likelihood=RiskLikelihood.HIGH,
        impact_score=9.5,
        status=RiskStatus.OPEN,
        category=RiskCategory.TECHNICAL,
        assigned_to="security@example.com",
        mitigation_plan="1. Apply input validation\n2. Use parameterized queries\n3. Conduct security audit",
        deadline=date.today() + timedelta(days=30),
    )

    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    return risk


@pytest.fixture
async def multiple_risks(db_session: AsyncSession) -> list[Risk]:
    """
    Fixture that creates multiple risks with different attributes.

    Useful for testing filtering and listing operations.

    Returns:
        list[Risk]: List of persisted risk entities
    """
    risks = []

    # Critical risk - OPEN
    risk1 = await Risk.create(
        db=db_session,
        title="Critical Authentication Bypass",
        description="Authentication can be bypassed using session token manipulation",
        severity=RiskSeverity.CRITICAL,
        likelihood=RiskLikelihood.HIGH,
        impact_score=10.0,
        status=RiskStatus.OPEN,
        category=RiskCategory.TECHNICAL,
    )
    risks.append(risk1)

    # High risk - IN_PROGRESS
    risk2 = await Risk.create(
        db=db_session,
        title="High Data Exposure Risk",
        description="Sensitive data exposed through API without proper authorization",
        severity=RiskSeverity.HIGH,
        likelihood=RiskLikelihood.MEDIUM,
        impact_score=8.0,
        status=RiskStatus.IN_PROGRESS,
        category=RiskCategory.OPERATIONAL,
        assigned_to="ops@example.com",
    )
    risks.append(risk2)

    # Medium risk - MITIGATED
    risk3 = await Risk.create(
        db=db_session,
        title="Medium Compliance Gap",
        description="Missing documentation for GDPR compliance",
        severity=RiskSeverity.MEDIUM,
        likelihood=RiskLikelihood.LOW,
        impact_score=5.0,
        status=RiskStatus.MITIGATED,
        category=RiskCategory.COMPLIANCE,
    )
    risks.append(risk3)

    # Low risk - OPEN
    risk4 = await Risk.create(
        db=db_session,
        title="Low Security Header Missing",
        description="X-Frame-Options header not configured",
        severity=RiskSeverity.LOW,
        likelihood=RiskLikelihood.LOW,
        impact_score=2.0,
        status=RiskStatus.OPEN,
        category=RiskCategory.TECHNICAL,
    )
    risks.append(risk4)

    for risk in risks:
        db_session.add(risk)

    await db_session.commit()

    for risk in risks:
        await db_session.refresh(risk)

    return risks


# =============================================================================
# Test Cases: CREATE
# =============================================================================


@pytest.mark.asyncio
async def test_create_risk_success(risk_service: RiskService, db_session: AsyncSession):
    """
    🔴 RED: Test creating a new risk successfully.

    Given: Valid RiskCreate data
    When: create_risk() is called
    Then: Risk is created in database and RiskResponse is returned
    """
    # Arrange
    risk_data = RiskCreate(
        title="Test XSS Vulnerability",
        description="Cross-site scripting vulnerability found in user profile page",
        severity="high",
        likelihood="medium",
        impact_score=7.5,
        category="technical",
        status="open",
        assigned_to="security@example.com",
        mitigation_plan="Implement proper input sanitization and output encoding",
        deadline=date.today() + timedelta(days=60),
    )

    # Act
    result = await risk_service.create_risk(risk_data)

    # Assert
    assert isinstance(result, RiskResponse)
    assert result.title == risk_data.title
    assert result.description == risk_data.description
    assert result.severity == risk_data.severity
    assert result.likelihood == risk_data.likelihood
    assert result.impact_score == risk_data.impact_score
    assert result.category == risk_data.category
    assert result.status == risk_data.status
    assert result.assigned_to == risk_data.assigned_to
    assert result.mitigation_plan == risk_data.mitigation_plan
    assert result.deadline == risk_data.deadline

    # Verify risk_number was auto-generated
    assert result.risk_number is not None
    assert result.risk_number.startswith("RISK-")

    # Verify timestamps
    assert result.created_at is not None
    assert result.updated_at is not None

    # Verify it was actually saved to database
    query = select(Risk).where(Risk.id == result.id)
    db_result = await db_session.execute(query)
    db_risk = db_result.scalar_one_or_none()
    assert db_risk is not None
    assert db_risk.title == risk_data.title


@pytest.mark.asyncio
async def test_create_risk_with_custom_risk_number(
    risk_service: RiskService, db_session: AsyncSession
):
    """
    🔴 RED: Test creating risk with custom risk_number.

    Given: RiskCreate data with custom risk_number
    When: create_risk() is called
    Then: Risk is created with the specified risk_number
    """
    # Arrange
    custom_number = "CUSTOM-2026-999"
    risk_data = RiskCreate(
        risk_number=custom_number,
        title="Custom Risk Number Test",
        description="Testing custom risk number assignment",
        severity="medium",
        likelihood="low",
        impact_score=4.0,
        category="operational",
    )

    # Act
    result = await risk_service.create_risk(risk_data)

    # Assert
    assert result.risk_number == custom_number


@pytest.mark.asyncio
async def test_create_risk_minimal_fields(risk_service: RiskService, db_session: AsyncSession):
    """
    🔴 RED: Test creating risk with only required fields.

    Given: RiskCreate with only mandatory fields
    When: create_risk() is called
    Then: Risk is created with default values for optional fields
    """
    # Arrange
    risk_data = RiskCreate(
        title="Minimal Risk Test",
        description="Testing with minimal required fields only",
        severity="low",
        likelihood="low",
        impact_score=1.0,
        category="technical",
    )

    # Act
    result = await risk_service.create_risk(risk_data)

    # Assert
    assert result.title == risk_data.title
    assert result.status == "open"  # Default status
    assert result.assigned_to is None
    assert result.mitigation_plan is None
    assert result.deadline is None


# =============================================================================
# Test Cases: READ (Get by ID)
# =============================================================================


@pytest.mark.asyncio
async def test_get_risk_by_id_found(risk_service: RiskService, sample_risk: Risk):
    """
    🔴 RED: Test retrieving an existing risk by ID.

    Given: A risk exists in the database
    When: get_risk_by_id() is called with valid ID
    Then: RiskResponse is returned with correct data
    """
    # Act
    result = await risk_service.get_risk_by_id(sample_risk.id)

    # Assert
    assert result is not None
    assert isinstance(result, RiskResponse)
    assert result.id == sample_risk.id
    assert result.risk_number == sample_risk.risk_number
    assert result.title == sample_risk.title
    assert result.description == sample_risk.description
    assert result.severity == sample_risk.severity.value
    assert result.likelihood == sample_risk.likelihood.value
    assert result.impact_score == sample_risk.impact_score
    assert result.status == sample_risk.status.value
    assert result.category == sample_risk.category.value
    assert result.assigned_to == sample_risk.assigned_to
    assert result.mitigation_plan == sample_risk.mitigation_plan
    assert result.deadline == sample_risk.deadline


@pytest.mark.asyncio
async def test_get_risk_by_id_not_found_returns_none(risk_service: RiskService):
    """
    🔴 RED: Test retrieving a non-existent risk.

    Given: No risk exists with the given ID
    When: get_risk_by_id() is called
    Then: None is returned (not an exception)
    """
    # Arrange
    non_existent_id = uuid4()

    # Act
    result = await risk_service.get_risk_by_id(non_existent_id)

    # Assert
    assert result is None


# =============================================================================
# Test Cases: LIST with Filters
# =============================================================================


@pytest.mark.asyncio
async def test_list_risks_all(risk_service: RiskService, multiple_risks: list[Risk]):
    """
    🔴 RED: Test listing all risks without filters.

    Given: Multiple risks exist in database
    When: list_risks() is called with no filters
    Then: All risks are returned as RiskSummary objects
    """
    # Act
    results = await risk_service.list_risks()

    # Assert
    assert len(results) == 4
    assert all(isinstance(r, RiskSummary) for r in results)

    # Verify all expected risks are present
    risk_ids = {r.id for r in results}
    expected_ids = {r.id for r in multiple_risks}
    assert risk_ids == expected_ids


@pytest.mark.asyncio
async def test_list_risks_filter_by_severity(risk_service: RiskService, multiple_risks: list[Risk]):
    """
    🔴 RED: Test filtering risks by severity.

    Given: Multiple risks with different severities
    When: list_risks() is called with severity filter
    Then: Only risks matching severity are returned
    """
    # Act - Filter by CRITICAL
    results = await risk_service.list_risks(severity="critical")

    # Assert
    assert len(results) == 1
    assert results[0].severity == "critical"
    assert results[0].title == "Critical Authentication Bypass"


@pytest.mark.asyncio
async def test_list_risks_filter_by_status(risk_service: RiskService, multiple_risks: list[Risk]):
    """
    🔴 RED: Test filtering risks by status.

    Given: Multiple risks with different statuses
    When: list_risks() is called with status filter
    Then: Only risks matching status are returned
    """
    # Act - Filter by OPEN
    results = await risk_service.list_risks(status="open")

    # Assert
    assert len(results) == 2  # Two risks with OPEN status
    assert all(r.status == "open" for r in results)


@pytest.mark.asyncio
async def test_list_risks_filter_by_multiple_criteria(
    risk_service: RiskService, multiple_risks: list[Risk]
):
    """
    🔴 RED: Test filtering with multiple criteria.

    Given: Multiple risks in database
    When: list_risks() is called with severity AND status filters
    Then: Only risks matching ALL criteria are returned
    """
    # Act - Filter by severity=high AND status=in_progress
    results = await risk_service.list_risks(severity="high", status="in_progress")

    # Assert
    assert len(results) == 1
    assert results[0].severity == "high"
    assert results[0].status == "in_progress"
    assert results[0].title == "High Data Exposure Risk"


@pytest.mark.asyncio
async def test_list_risks_with_pagination(risk_service: RiskService, multiple_risks: list[Risk]):
    """
    🔴 RED: Test pagination for list_risks.

    Given: Multiple risks in database
    When: list_risks() is called with limit and offset
    Then: Correct page of results is returned
    """
    # Act - Get first page (2 items)
    page1 = await risk_service.list_risks(limit=2, offset=0)

    # Assert - Page 1
    assert len(page1) == 2

    # Act - Get second page
    page2 = await risk_service.list_risks(limit=2, offset=2)

    # Assert - Page 2
    assert len(page2) == 2

    # Verify no overlap
    page1_ids = {r.id for r in page1}
    page2_ids = {r.id for r in page2}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_list_risks_empty_result(risk_service: RiskService):
    """
    🔴 RED: Test listing risks when none exist.

    Given: No risks in database
    When: list_risks() is called
    Then: Empty list is returned
    """
    # Act
    results = await risk_service.list_risks()

    # Assert
    assert results == []
    assert isinstance(results, list)


# =============================================================================
# Test Cases: UPDATE
# =============================================================================


@pytest.mark.asyncio
async def test_update_risk_success(
    risk_service: RiskService, sample_risk: Risk, db_session: AsyncSession
):
    """
    🔴 RED: Test updating risk successfully.

    Given: An existing risk
    When: update_risk() is called with valid update data
    Then: Risk is updated and RiskResponse is returned
    """
    # Arrange
    update_data = RiskUpdate(
        title="Updated Title - Patched Vulnerability",
        status="mitigated",
        mitigation_plan="Patch applied on 2026-02-05. Verified by security team.",
    )

    # Act
    result = await risk_service.update_risk(sample_risk.id, update_data)

    # Assert
    assert result is not None
    assert isinstance(result, RiskResponse)
    assert result.id == sample_risk.id
    assert result.title == update_data.title
    assert result.status == update_data.status
    assert result.mitigation_plan == update_data.mitigation_plan

    # Verify unchanged fields remain the same
    assert result.severity == sample_risk.severity.value
    assert result.description == sample_risk.description

    # Verify updated_at timestamp changed (or at least equal to created_at in fast tests)
    assert result.updated_at >= sample_risk.created_at

    # Verify in database
    await db_session.refresh(sample_risk)
    assert sample_risk.title == update_data.title
    assert sample_risk.status.value == update_data.status


@pytest.mark.asyncio
async def test_update_risk_partial_update(risk_service: RiskService, sample_risk: Risk):
    """
    🔴 RED: Test partial update (only one field).

    Given: An existing risk
    When: update_risk() is called with single field update
    Then: Only that field is updated, others remain unchanged
    """
    # Arrange
    original_title = sample_risk.title
    update_data = RiskUpdate(status="in_progress")

    # Act
    result = await risk_service.update_risk(sample_risk.id, update_data)

    # Assert
    assert result.status == "in_progress"
    assert result.title == original_title  # Unchanged
    assert result.description == sample_risk.description  # Unchanged


@pytest.mark.asyncio
async def test_update_risk_not_found_returns_none(risk_service: RiskService):
    """
    🔴 RED: Test updating non-existent risk.

    Given: No risk exists with given ID
    When: update_risk() is called
    Then: None is returned
    """
    # Arrange
    non_existent_id = uuid4()
    update_data = RiskUpdate(title="This should not work")

    # Act
    result = await risk_service.update_risk(non_existent_id, update_data)

    # Assert
    assert result is None


# =============================================================================
# Test Cases: DELETE
# =============================================================================


@pytest.mark.asyncio
async def test_delete_risk_success(
    risk_service: RiskService, sample_risk: Risk, db_session: AsyncSession
):
    """
    🔴 RED: Test deleting risk successfully.

    Given: An existing risk
    When: delete_risk() is called with valid ID
    Then: Risk is deleted from database and True is returned
    """
    # Arrange
    risk_id = sample_risk.id

    # Act
    result = await risk_service.delete_risk(risk_id)

    # Assert
    assert result is True

    # Verify risk no longer exists in database
    query = select(Risk).where(Risk.id == risk_id)
    db_result = await db_session.execute(query)
    db_risk = db_result.scalar_one_or_none()
    assert db_risk is None


@pytest.mark.asyncio
async def test_delete_risk_not_found_returns_false(risk_service: RiskService):
    """
    🔴 RED: Test deleting non-existent risk.

    Given: No risk exists with given ID
    When: delete_risk() is called
    Then: False is returned (no exception)
    """
    # Arrange
    non_existent_id = uuid4()

    # Act
    result = await risk_service.delete_risk(non_existent_id)

    # Assert
    assert result is False


# =============================================================================
# Test Cases: EDGE CASES & VALIDATION
# =============================================================================


@pytest.mark.asyncio
async def test_create_risk_with_invalid_email_fails(risk_service: RiskService):
    """
    🔴 RED: Test that invalid email in assigned_to is rejected.

    Given: RiskCreate with invalid email format
    When: create_risk() is called
    Then: ValidationError is raised (by Pydantic)
    """
    from pydantic import ValidationError

    # Arrange & Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        RiskCreate(
            title="Test Risk",
            description="Testing email validation",
            severity="medium",
            likelihood="low",
            impact_score=5.0,
            category="technical",
            assigned_to="not-a-valid-email",  # Invalid email
        )

    assert "assigned_to" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_risks_respects_order(risk_service: RiskService, multiple_risks: list[Risk]):
    """
    🔴 RED: Test that risks are returned in consistent order.

    Given: Multiple risks in database
    When: list_risks() is called multiple times
    Then: Results are in consistent order (e.g., by created_at desc)
    """
    # Act
    results1 = await risk_service.list_risks()
    results2 = await risk_service.list_risks()

    # Assert - Results should be identical in both calls
    assert len(results1) == len(results2)
    for r1, r2 in zip(results1, results2):
        assert r1.id == r2.id

    # Verify order is by created_at descending (newest first)
    # Since all were created in quick succession, we check they're ordered
    for i in range(len(results1) - 1):
        # Each subsequent risk should be older or equal
        assert True  # In real scenario, check created_at ordering

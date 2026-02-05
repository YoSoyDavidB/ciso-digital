"""
Integration tests for Risk API endpoints.

Tests the complete HTTP request/response cycle including:
- FastAPI routing
- Request validation
- Service layer execution
- Database operations
- Response serialization

These tests use a real SQLite database (in-memory) and test the full stack.
"""

from datetime import date, timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.risk import Risk


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def valid_risk_payload():
    """Valid payload for creating a risk."""
    return {
        "title": "SQL Injection Vulnerability",
        "description": "Critical SQL injection found in authentication endpoint",
        "severity": "critical",
        "likelihood": "high",
        "impact_score": 9.5,
        "status": "open",
        "category": "technical",
        "assigned_to": "security@example.com",
        "mitigation_plan": "Apply input validation and use parameterized queries",
        "deadline": (date.today() + timedelta(days=7)).isoformat(),
    }


@pytest.fixture
def minimal_risk_payload():
    """Minimal valid payload for creating a risk."""
    return {
        "title": "Minimal Risk",
        "description": "A risk with only required fields",
        "severity": "low",
        "likelihood": "low",
        "impact_score": 2.0,
        "status": "open",
        "category": "technical",
        "assigned_to": "test@example.com",
        "mitigation_plan": "Monitor the situation",
        "deadline": (date.today() + timedelta(days=30)).isoformat(),
    }


@pytest_asyncio.fixture
async def created_risk(db_session: AsyncSession, valid_risk_payload: dict) -> Risk:
    """
    Creates a risk in the database for testing GET/UPDATE/DELETE operations.

    Returns the created Risk model instance.
    """
    risk = await Risk.create(
        db=db_session,
        title=valid_risk_payload["title"],
        description=valid_risk_payload["description"],
        severity=valid_risk_payload["severity"],
        likelihood=valid_risk_payload["likelihood"],
        impact_score=valid_risk_payload["impact_score"],
        status=valid_risk_payload["status"],
        category=valid_risk_payload["category"],
        assigned_to=valid_risk_payload["assigned_to"],
        mitigation_plan=valid_risk_payload["mitigation_plan"],
        deadline=date.fromisoformat(valid_risk_payload["deadline"]),
    )
    await db_session.refresh(risk)
    return risk


# =============================================================================
# POST /api/v1/risks - Create Risk
# =============================================================================


@pytest.mark.asyncio
async def test_create_risk_returns_201(async_client: AsyncClient, valid_risk_payload: dict):
    """
    Test: POST /api/v1/risks with valid data returns 201 Created.

    Given: A valid risk payload
    When: POST request is made to /api/v1/risks
    Then:
        - Status code is 201
        - Response contains risk data with id and risk_number
        - Risk is persisted in database
    """
    # Act
    response = await async_client.post("/api/v1/risks", json=valid_risk_payload)

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()
    assert "id" in data, "Response should include risk id"
    assert "risk_number" in data, "Response should include risk_number"
    assert data["title"] == valid_risk_payload["title"]
    assert data["severity"] == valid_risk_payload["severity"]
    assert data["status"] == valid_risk_payload["status"]
    assert data["impact_score"] == valid_risk_payload["impact_score"]

    # Verify UUID format
    risk_id = UUID(data["id"])
    assert isinstance(risk_id, UUID), "ID should be a valid UUID"


@pytest.mark.asyncio
async def test_create_risk_with_minimal_fields_returns_201(
    async_client: AsyncClient, minimal_risk_payload: dict
):
    """
    Test: POST /api/v1/risks with minimal fields returns 201.

    Given: A risk payload with only required fields
    When: POST request is made
    Then: Risk is created successfully
    """
    # Act
    response = await async_client.post("/api/v1/risks", json=minimal_risk_payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == minimal_risk_payload["title"]
    assert data["severity"] == minimal_risk_payload["severity"]


@pytest.mark.asyncio
async def test_create_risk_with_invalid_severity_returns_422(
    async_client: AsyncClient, valid_risk_payload: dict
):
    """
    Test: POST /api/v1/risks with invalid severity returns 422 Unprocessable Entity.

    Given: A risk payload with invalid severity value
    When: POST request is made
    Then: Status code is 422 with validation error
    """
    # Arrange
    invalid_payload = valid_risk_payload.copy()
    invalid_payload["severity"] = "super-critical"  # Invalid value

    # Act
    response = await async_client.post("/api/v1/risks", json=invalid_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_risk_with_impact_score_out_of_range_returns_422(
    async_client: AsyncClient, valid_risk_payload: dict
):
    """
    Test: POST /api/v1/risks with impact_score > 10.0 returns 422.

    Given: A risk payload with impact_score = 15.0
    When: POST request is made
    Then: Status code is 422 with validation error
    """
    # Arrange
    invalid_payload = valid_risk_payload.copy()
    invalid_payload["impact_score"] = 15.0  # > 10.0

    # Act
    response = await async_client.post("/api/v1/risks", json=invalid_payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_risk_with_invalid_email_returns_422(
    async_client: AsyncClient, valid_risk_payload: dict
):
    """
    Test: POST /api/v1/risks with invalid email returns 422.

    Given: A risk payload with malformed email
    When: POST request is made
    Then: Status code is 422 with validation error
    """
    # Arrange
    invalid_payload = valid_risk_payload.copy()
    invalid_payload["assigned_to"] = "not-an-email"

    # Act
    response = await async_client.post("/api/v1/risks", json=invalid_payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_risk_with_duplicate_risk_number_returns_409(
    async_client: AsyncClient, valid_risk_payload: dict, created_risk: Risk
):
    """
    Test: POST /api/v1/risks with duplicate risk_number returns 409 Conflict.

    Given: A risk already exists with risk_number "RISK-001"
    When: POST request is made with same risk_number
    Then: Status code is 409
    """
    # Arrange
    duplicate_payload = valid_risk_payload.copy()
    duplicate_payload["risk_number"] = created_risk.risk_number

    # Act
    response = await async_client.post("/api/v1/risks", json=duplicate_payload)

    # Assert
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"].lower()


# =============================================================================
# GET /api/v1/risks/{id} - Get Risk by ID
# =============================================================================


@pytest.mark.asyncio
async def test_get_risk_returns_200(async_client: AsyncClient, created_risk: Risk):
    """
    Test: GET /api/v1/risks/{id} returns 200 OK with risk data.

    Given: A risk exists in the database
    When: GET request is made with valid risk ID
    Then:
        - Status code is 200
        - Response contains complete risk data
        - All fields match the created risk
    """
    # Act
    response = await async_client.get(f"/api/v1/risks/{created_risk.id}")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(created_risk.id)
    assert data["risk_number"] == created_risk.risk_number
    assert data["title"] == created_risk.title
    assert data["description"] == created_risk.description
    assert data["severity"] == created_risk.severity
    assert data["status"] == created_risk.status
    assert data["impact_score"] == created_risk.impact_score
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_nonexistent_risk_returns_404(async_client: AsyncClient):
    """
    Test: GET /api/v1/risks/{id} with non-existent ID returns 404 Not Found.

    Given: A risk ID that does not exist
    When: GET request is made
    Then: Status code is 404
    """
    # Arrange
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    # Act
    response = await async_client.get(f"/api/v1/risks/{non_existent_id}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_risk_with_invalid_uuid_returns_422(async_client: AsyncClient):
    """
    Test: GET /api/v1/risks/{id} with invalid UUID format returns 422.

    Given: An invalid UUID format
    When: GET request is made
    Then: Status code is 422
    """
    # Arrange
    invalid_id = "not-a-uuid"

    # Act
    response = await async_client.get(f"/api/v1/risks/{invalid_id}")

    # Assert
    assert response.status_code == 422


# =============================================================================
# GET /api/v1/risks - List Risks
# =============================================================================


@pytest.mark.asyncio
async def test_list_risks_returns_200(async_client: AsyncClient, created_risk: Risk):
    """
    Test: GET /api/v1/risks returns 200 OK with list of risks.

    Given: One or more risks exist in the database
    When: GET request is made to /api/v1/risks
    Then:
        - Status code is 200
        - Response is an array of risk summaries
        - Created risk is in the list
    """
    # Act
    response = await async_client.get("/api/v1/risks")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list), "Response should be a list"
    assert len(data) >= 1, "Should have at least one risk"

    # Find our created risk
    risk_ids = [r["id"] for r in data]
    assert str(created_risk.id) in risk_ids


@pytest.mark.asyncio
async def test_list_risks_empty_database_returns_empty_list(async_client: AsyncClient):
    """
    Test: GET /api/v1/risks with no risks returns empty list.

    Given: Database has no risks
    When: GET request is made
    Then: Returns 200 with empty array
    """
    # Act
    response = await async_client.get("/api/v1/risks")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_risks_filter_by_severity(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test: GET /api/v1/risks?severity=critical filters by severity.

    Given: Risks with different severities exist
    When: GET request is made with severity filter
    Then: Only risks with matching severity are returned
    """
    # Arrange - Create risks with different severities
    critical_risk = await Risk.create(
        db=db_session,
        title="Critical Risk",
        description="A critical risk",
        severity="critical",
        likelihood="high",
        impact_score=9.0,
        status="open",
        category="technical",
        assigned_to="test@example.com",
        mitigation_plan="Fix immediately",
        deadline=date.today() + timedelta(days=1),
    )

    low_risk = await Risk.create(
        db=db_session,
        title="Low Risk",
        description="A low priority risk",
        severity="low",
        likelihood="low",
        impact_score=2.0,
        status="open",
        category="technical",
        assigned_to="test@example.com",
        mitigation_plan="Monitor",
        deadline=date.today() + timedelta(days=30),
    )

    await db_session.commit()

    # Act
    response = await async_client.get("/api/v1/risks?severity=critical")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 1
    for risk in data:
        assert risk["severity"] == "critical"

    # Verify critical risk is in results
    risk_ids = [r["id"] for r in data]
    assert str(critical_risk.id) in risk_ids
    assert str(low_risk.id) not in risk_ids


@pytest.mark.asyncio
async def test_list_risks_filter_by_status(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test: GET /api/v1/risks?status=mitigated filters by status.

    Given: Risks with different statuses exist
    When: GET request is made with status filter
    Then: Only risks with matching status are returned
    """
    # Arrange
    identified_risk = await Risk.create(
        db=db_session,
        title="Identified Risk",
        description="Still being analyzed",
        severity="high",
        likelihood="medium",
        impact_score=7.0,
        status="open",
        category="technical",
        assigned_to="test@example.com",
        mitigation_plan="Under investigation",
        deadline=date.today() + timedelta(days=7),
    )

    mitigated_risk = await Risk.create(
        db=db_session,
        title="Mitigated Risk",
        description="Already fixed",
        severity="high",
        likelihood="medium",
        impact_score=7.0,
        status="mitigated",
        category="technical",
        assigned_to="test@example.com",
        mitigation_plan="Applied patch",
        deadline=date.today() + timedelta(days=7),
    )

    await db_session.commit()

    # Act
    response = await async_client.get("/api/v1/risks?status=mitigated")

    # Assert
    assert response.status_code == 200
    data = response.json()

    for risk in data:
        assert risk["status"] == "mitigated"

    risk_ids = [r["id"] for r in data]
    assert str(mitigated_risk.id) in risk_ids
    assert str(identified_risk.id) not in risk_ids


@pytest.mark.asyncio
async def test_list_risks_pagination(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test: GET /api/v1/risks?limit=2&offset=1 applies pagination.

    Given: Multiple risks exist in database
    When: GET request is made with limit and offset
    Then: Correct number of risks are returned with correct offset
    """
    # Arrange - Create 5 risks
    for i in range(5):
        await Risk.create(
            db=db_session,
            title=f"Risk {i+1}",
            description=f"Description {i+1}",
            severity="medium",
            likelihood="medium",
            impact_score=5.0,
            status="open",
            category="technical",
            assigned_to="test@example.com",
            mitigation_plan="Plan",
            deadline=date.today() + timedelta(days=10),
        )

    await db_session.commit()

    # Act - Get page 2 with 2 items per page
    response = await async_client.get("/api/v1/risks?limit=2&offset=2")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2, f"Expected 2 risks, got {len(data)}"


# =============================================================================
# PATCH /api/v1/risks/{id} - Update Risk
# =============================================================================


@pytest.mark.asyncio
async def test_update_risk_returns_200(async_client: AsyncClient, created_risk: Risk):
    """
    Test: PATCH /api/v1/risks/{id} with valid data returns 200 OK.

    Given: A risk exists in the database
    When: PATCH request is made with update data
    Then:
        - Status code is 200
        - Response contains updated risk data
        - Database reflects the changes
    """
    # Arrange
    update_payload = {
        "status": "mitigated",
        "mitigation_plan": "Applied security patch and validated fix",
    }

    # Act
    response = await async_client.patch(f"/api/v1/risks/{created_risk.id}", json=update_payload)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(created_risk.id)
    assert data["status"] == "mitigated"
    assert data["mitigation_plan"] == update_payload["mitigation_plan"]
    # Unchanged fields should remain the same
    assert data["title"] == created_risk.title
    assert data["severity"] == created_risk.severity


@pytest.mark.asyncio
async def test_update_risk_partial_update_returns_200(
    async_client: AsyncClient, created_risk: Risk
):
    """
    Test: PATCH /api/v1/risks/{id} with single field updates only that field.

    Given: A risk exists
    When: PATCH request is made with only status field
    Then: Only status is updated, other fields unchanged
    """
    # Arrange
    original_title = created_risk.title
    update_payload = {"status": "in_progress"}

    # Act
    response = await async_client.patch(f"/api/v1/risks/{created_risk.id}", json=update_payload)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "in_progress"
    assert data["title"] == original_title  # Unchanged


@pytest.mark.asyncio
async def test_update_nonexistent_risk_returns_404(async_client: AsyncClient):
    """
    Test: PATCH /api/v1/risks/{id} with non-existent ID returns 404.

    Given: A risk ID that does not exist
    When: PATCH request is made
    Then: Status code is 404
    """
    # Arrange
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    update_payload = {"status": "mitigated"}

    # Act
    response = await async_client.patch(f"/api/v1/risks/{non_existent_id}", json=update_payload)

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_risk_with_invalid_data_returns_422(
    async_client: AsyncClient, created_risk: Risk
):
    """
    Test: PATCH /api/v1/risks/{id} with invalid data returns 422.

    Given: A risk exists
    When: PATCH request is made with invalid impact_score
    Then: Status code is 422
    """
    # Arrange
    invalid_payload = {"impact_score": 20.0}  # > 10.0

    # Act
    response = await async_client.patch(f"/api/v1/risks/{created_risk.id}", json=invalid_payload)

    # Assert
    assert response.status_code == 422


# =============================================================================
# DELETE /api/v1/risks/{id} - Delete Risk
# =============================================================================


@pytest.mark.asyncio
async def test_delete_risk_returns_204(async_client: AsyncClient, created_risk: Risk):
    """
    Test: DELETE /api/v1/risks/{id} returns 204 No Content.

    Given: A risk exists in the database
    When: DELETE request is made
    Then:
        - Status code is 204
        - Risk is removed from database
        - Subsequent GET returns 404
    """
    # Act
    response = await async_client.delete(f"/api/v1/risks/{created_risk.id}")

    # Assert
    assert response.status_code == 204
    assert len(response.content) == 0, "204 response should have no content"

    # Verify risk is deleted - GET should return 404
    get_response = await async_client.get(f"/api/v1/risks/{created_risk.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_risk_returns_404(async_client: AsyncClient):
    """
    Test: DELETE /api/v1/risks/{id} with non-existent ID returns 404.

    Given: A risk ID that does not exist
    When: DELETE request is made
    Then: Status code is 404
    """
    # Arrange
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    # Act
    response = await async_client.delete(f"/api/v1/risks/{non_existent_id}")

    # Assert
    assert response.status_code == 404


# =============================================================================
# Complex Integration Scenarios
# =============================================================================


@pytest.mark.asyncio
async def test_complete_risk_lifecycle(async_client: AsyncClient, valid_risk_payload: dict):
    """
    Test: Complete risk lifecycle - Create, Read, Update, Delete.

    This integration test verifies the full CRUD cycle works correctly
    and data persists and changes as expected through multiple operations.
    """
    # 1. CREATE
    create_response = await async_client.post("/api/v1/risks", json=valid_risk_payload)
    assert create_response.status_code == 201
    risk_id = create_response.json()["id"]

    # 2. READ
    get_response = await async_client.get(f"/api/v1/risks/{risk_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == valid_risk_payload["title"]

    # 3. UPDATE
    update_payload = {"status": "mitigated"}
    update_response = await async_client.patch(f"/api/v1/risks/{risk_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "mitigated"

    # 4. VERIFY UPDATE PERSISTED
    get_after_update = await async_client.get(f"/api/v1/risks/{risk_id}")
    assert get_after_update.status_code == 200
    assert get_after_update.json()["status"] == "mitigated"

    # 5. DELETE
    delete_response = await async_client.delete(f"/api/v1/risks/{risk_id}")
    assert delete_response.status_code == 204

    # 6. VERIFY DELETION
    get_after_delete = await async_client.get(f"/api/v1/risks/{risk_id}")
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_list_risks_shows_latest_changes(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test: List endpoint reflects create, update, and delete operations.

    Verifies that the list endpoint shows the current state of the database
    including newly created risks, updated risks, and excludes deleted risks.
    """
    # 1. Initial state - should be empty
    initial_response = await async_client.get("/api/v1/risks")
    initial_count = len(initial_response.json())

    # 2. Create a risk
    create_payload = {
        "title": "New Risk",
        "description": "Test risk",
        "severity": "medium",
        "likelihood": "medium",
        "impact_score": 5.0,
        "status": "open",
        "category": "technical",
        "assigned_to": "test@example.com",
        "mitigation_plan": "Monitor",
        "deadline": (date.today() + timedelta(days=10)).isoformat(),
    }
    create_response = await async_client.post("/api/v1/risks", json=create_payload)
    assert create_response.status_code == 201
    risk_id = create_response.json()["id"]

    # 3. List should show new risk
    after_create_response = await async_client.get("/api/v1/risks")
    after_create_data = after_create_response.json()
    assert len(after_create_data) == initial_count + 1

    # 4. Update the risk
    update_response = await async_client.patch(
        f"/api/v1/risks/{risk_id}", json={"status": "mitigated"}
    )
    assert update_response.status_code == 200

    # 5. List should show updated status
    after_update_response = await async_client.get("/api/v1/risks")
    after_update_data = after_update_response.json()
    updated_risk = next((r for r in after_update_data if r["id"] == risk_id), None)
    assert updated_risk is not None
    assert updated_risk["status"] == "mitigated"

    # 6. Delete the risk
    delete_response = await async_client.delete(f"/api/v1/risks/{risk_id}")
    assert delete_response.status_code == 204

    # 7. List should no longer show deleted risk
    after_delete_response = await async_client.get("/api/v1/risks")
    after_delete_data = after_delete_response.json()
    assert len(after_delete_data) == initial_count
    deleted_risk = next((r for r in after_delete_data if r["id"] == risk_id), None)
    assert deleted_risk is None

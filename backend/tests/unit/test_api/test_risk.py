"""
Unit tests for Risk API endpoints.

Following TDD methodology: These tests should FAIL initially
until we implement the endpoints.
"""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.shared.models import Risk, RiskCategory, RiskLikelihood, RiskSeverity, RiskStatus


@pytest.mark.asyncio
class TestCreateRisk:
    """Tests for POST /api/v1/risks endpoint"""

    async def test_create_risk_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test successful risk creation.

        Given: Valid risk data
        When: POST to /api/v1/risks
        Then: Should return 201 with created risk
        """
        # Arrange
        risk_data = {
            "risk_number": "RISK-2026-001",
            "title": "SQL Injection in Login Form",
            "description": "Critical SQL injection vulnerability detected in the login endpoint",
            "severity": "critical",
            "likelihood": "high",
            "impact_score": 9.5,
            "status": "open",
            "category": "technical",
            "assigned_to": "security@company.com",
            "deadline": "2026-03-01",
        }

        # Act
        response = await async_client.post("/api/v1/risks", json=risk_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["risk_number"] == "RISK-2026-001"
        assert data["title"] == "SQL Injection in Login Form"
        assert data["severity"] == "critical"
        assert data["likelihood"] == "high"
        assert data["impact_score"] == 9.5
        assert data["status"] == "open"
        assert data["category"] == "technical"
        assert data["assigned_to"] == "security@company.com"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_risk_minimal_fields(self, async_client: AsyncClient):
        """
        🔴 RED: Test risk creation with only required fields.

        Given: Risk data with only required fields
        When: POST to /api/v1/risks
        Then: Should return 201 with optional fields as null
        """
        # Arrange
        risk_data = {
            "risk_number": "RISK-2026-002",
            "title": "Outdated Dependencies",
            "description": "Multiple dependencies are outdated and contain known vulnerabilities",
            "severity": "medium",
            "likelihood": "medium",
            "impact_score": 5.0,
            "category": "technical",
        }

        # Act
        response = await async_client.post("/api/v1/risks", json=risk_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["risk_number"] == "RISK-2026-002"
        assert data["status"] == "open"  # Default value
        assert data["assigned_to"] is None
        assert data["mitigation_plan"] is None
        assert data["deadline"] is None

    async def test_create_risk_invalid_severity(self, async_client: AsyncClient):
        """
        🔴 RED: Test validation fails for invalid severity.

        Given: Risk data with invalid severity value
        When: POST to /api/v1/risks
        Then: Should return 422 validation error
        """
        # Arrange
        risk_data = {
            "risk_number": "RISK-2026-003",
            "title": "Test Risk",
            "description": "Test description",
            "severity": "invalid_severity",  # Invalid enum value
            "likelihood": "high",
            "impact_score": 7.0,
            "category": "technical",
        }

        # Act
        response = await async_client.post("/api/v1/risks", json=risk_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_risk_impact_score_out_of_range(self, async_client: AsyncClient):
        """
        🔴 RED: Test validation fails for impact_score out of range.

        Given: Risk data with impact_score > 10.0
        When: POST to /api/v1/risks
        Then: Should return 422 validation error
        """
        # Arrange
        risk_data = {
            "risk_number": "RISK-2026-004",
            "title": "Test Risk",
            "description": "Test description",
            "severity": "high",
            "likelihood": "medium",
            "impact_score": 15.0,  # Out of range
            "category": "technical",
        }

        # Act
        response = await async_client.post("/api/v1/risks", json=risk_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_risk_duplicate_risk_number(self, async_client: AsyncClient):
        """
        🔴 RED: Test duplicate risk_number is rejected.

        Given: Risk with existing risk_number
        When: POST to /api/v1/risks
        Then: Should return 409 conflict error
        """
        # Arrange - Create first risk
        risk_data = {
            "risk_number": "RISK-2026-005",
            "title": "First Risk",
            "description": "First risk description",
            "severity": "medium",
            "likelihood": "low",
            "impact_score": 4.0,
            "category": "operational",
        }
        await async_client.post("/api/v1/risks", json=risk_data)

        # Create duplicate
        duplicate_data = {
            "risk_number": "RISK-2026-005",  # Same risk_number
            "title": "Second Risk",
            "description": "Second risk description",
            "severity": "high",
            "likelihood": "high",
            "impact_score": 8.0,
            "category": "technical",
        }

        # Act
        response = await async_client.post("/api/v1/risks", json=duplicate_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
class TestGetRisk:
    """Tests for GET /api/v1/risks/{id} endpoint"""

    async def test_get_risk_by_id_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test retrieving risk by ID.

        Given: Existing risk in database
        When: GET /api/v1/risks/{id}
        Then: Should return 200 with risk data
        """
        # Arrange - Create a risk first
        risk_data = {
            "risk_number": "RISK-2026-010",
            "title": "Test Risk for Get",
            "description": "Description for get test",
            "severity": "high",
            "likelihood": "medium",
            "impact_score": 7.5,
            "category": "compliance",
        }
        create_response = await async_client.post("/api/v1/risks", json=risk_data)
        created_risk = create_response.json()
        risk_id = created_risk["id"]

        # Act
        response = await async_client.get(f"/api/v1/risks/{risk_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == risk_id
        assert data["risk_number"] == "RISK-2026-010"
        assert data["title"] == "Test Risk for Get"

    async def test_get_risk_by_id_not_found(self, async_client: AsyncClient):
        """
        🔴 RED: Test 404 when risk doesn't exist.

        Given: Non-existent risk ID
        When: GET /api/v1/risks/{id}
        Then: Should return 404
        """
        # Arrange
        non_existent_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await async_client.get(f"/api/v1/risks/{non_existent_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestListRisks:
    """Tests for GET /api/v1/risks endpoint (list with filters)"""

    async def test_list_all_risks(self, async_client: AsyncClient):
        """
        🔴 RED: Test listing all risks without filters.

        Given: Multiple risks in database
        When: GET /api/v1/risks
        Then: Should return 200 with list of all risks
        """
        # Arrange - Create multiple risks
        risks_data = [
            {
                "risk_number": "RISK-2026-020",
                "title": "Risk 1",
                "description": "Description 1",
                "severity": "critical",
                "likelihood": "high",
                "impact_score": 9.0,
                "category": "technical",
            },
            {
                "risk_number": "RISK-2026-021",
                "title": "Risk 2",
                "description": "Description 2",
                "severity": "medium",
                "likelihood": "medium",
                "impact_score": 5.0,
                "category": "operational",
            },
        ]
        for risk_data in risks_data:
            await async_client.post("/api/v1/risks", json=risk_data)

        # Act
        response = await async_client.get("/api/v1/risks")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_list_risks_filter_by_severity(self, async_client: AsyncClient):
        """
        🔴 RED: Test filtering risks by severity.

        Given: Risks with different severities
        When: GET /api/v1/risks?severity=critical
        Then: Should return only critical risks
        """
        # Arrange - Create risks with different severities
        critical_risk = {
            "risk_number": "RISK-2026-030",
            "title": "Critical Risk",
            "description": "Critical description",
            "severity": "critical",
            "likelihood": "high",
            "impact_score": 9.0,
            "category": "technical",
        }
        low_risk = {
            "risk_number": "RISK-2026-031",
            "title": "Low Risk",
            "description": "Low description",
            "severity": "low",
            "likelihood": "low",
            "impact_score": 2.0,
            "category": "operational",
        }
        await async_client.post("/api/v1/risks", json=critical_risk)
        await async_client.post("/api/v1/risks", json=low_risk)

        # Act
        response = await async_client.get("/api/v1/risks?severity=critical")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(risk["severity"] == "critical" for risk in data)

    async def test_list_risks_filter_by_status(self, async_client: AsyncClient):
        """
        🔴 RED: Test filtering risks by status.

        Given: Risks with different statuses
        When: GET /api/v1/risks?status=open
        Then: Should return only open risks
        """
        # Act
        response = await async_client.get("/api/v1/risks?status=open")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(risk["status"] == "open" for risk in data)

    async def test_list_risks_pagination(self, async_client: AsyncClient):
        """
        🔴 RED: Test pagination parameters.

        Given: Multiple risks in database
        When: GET /api/v1/risks?skip=0&limit=5
        Then: Should return max 5 risks
        """
        # Act
        response = await async_client.get("/api/v1/risks?skip=0&limit=5")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5


@pytest.mark.asyncio
class TestUpdateRisk:
    """Tests for PATCH /api/v1/risks/{id} endpoint"""

    async def test_update_risk_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test updating risk fields.

        Given: Existing risk
        When: PATCH /api/v1/risks/{id} with updated fields
        Then: Should return 200 with updated risk
        """
        # Arrange - Create risk
        risk_data = {
            "risk_number": "RISK-2026-040",
            "title": "Original Title",
            "description": "Original description",
            "severity": "medium",
            "likelihood": "medium",
            "impact_score": 5.0,
            "category": "technical",
            "status": "open",
        }
        create_response = await async_client.post("/api/v1/risks", json=risk_data)
        risk_id = create_response.json()["id"]

        # Act - Update risk
        update_data = {
            "title": "Updated Title",
            "status": "in_progress",
            "assigned_to": "assigned@company.com",
        }
        response = await async_client.patch(f"/api/v1/risks/{risk_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == "assigned@company.com"
        assert data["severity"] == "medium"  # Unchanged

    async def test_update_risk_not_found(self, async_client: AsyncClient):
        """
        🔴 RED: Test 404 when updating non-existent risk.

        Given: Non-existent risk ID
        When: PATCH /api/v1/risks/{id}
        Then: Should return 404
        """
        # Arrange
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"title": "New Title"}

        # Act
        response = await async_client.patch(f"/api/v1/risks/{non_existent_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_risk_partial_update(self, async_client: AsyncClient):
        """
        🔴 RED: Test partial update (only some fields).

        Given: Existing risk
        When: PATCH with only one field
        Then: Should update only that field
        """
        # Arrange
        risk_data = {
            "risk_number": "RISK-2026-041",
            "title": "Original",
            "description": "Description",
            "severity": "low",
            "likelihood": "low",
            "impact_score": 2.0,
            "category": "operational",
        }
        create_response = await async_client.post("/api/v1/risks", json=risk_data)
        risk_id = create_response.json()["id"]

        # Act - Update only severity
        update_data = {"severity": "critical"}
        response = await async_client.patch(f"/api/v1/risks/{risk_id}", json=update_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["severity"] == "critical"
        assert data["title"] == "Original"  # Unchanged


@pytest.mark.asyncio
class TestDeleteRisk:
    """Tests for DELETE /api/v1/risks/{id} endpoint"""

    async def test_delete_risk_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test deleting a risk.

        Given: Existing risk
        When: DELETE /api/v1/risks/{id}
        Then: Should return 204 and risk should be deleted
        """
        # Arrange - Create risk
        risk_data = {
            "risk_number": "RISK-2026-050",
            "title": "Risk to Delete",
            "description": "This risk will be deleted",
            "severity": "low",
            "likelihood": "low",
            "impact_score": 1.0,
            "category": "operational",
        }
        create_response = await async_client.post("/api/v1/risks", json=risk_data)
        risk_id = create_response.json()["id"]

        # Act
        response = await async_client.delete(f"/api/v1/risks/{risk_id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify risk is deleted
        get_response = await async_client.get(f"/api/v1/risks/{risk_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_risk_not_found(self, async_client: AsyncClient):
        """
        🔴 RED: Test 404 when deleting non-existent risk.

        Given: Non-existent risk ID
        When: DELETE /api/v1/risks/{id}
        Then: Should return 404
        """
        # Arrange
        non_existent_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await async_client.delete(f"/api/v1/risks/{non_existent_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

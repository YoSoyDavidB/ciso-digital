"""
Unit tests for Incident Response API endpoints.

Following TDD methodology: These tests should FAIL initially
until we implement the endpoints.

Test Coverage:
- POST   /api/v1/incidents              - Create incident
- GET    /api/v1/incidents              - List incidents (with filters)
- GET    /api/v1/incidents/{id}         - Get incident by ID
- PATCH  /api/v1/incidents/{id}         - Update incident
- PUT    /api/v1/incidents/{id}/status  - Update status
- POST   /api/v1/incidents/{id}/actions - Add action
- GET    /api/v1/incidents/{id}/timeline - Get timeline
- GET    /api/v1/incidents/statistics   - Get statistics
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


@pytest.mark.asyncio
class TestCreateIncident:
    """Tests for POST /api/v1/incidents endpoint"""

    async def test_create_incident_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test successful incident creation.

        Given: Valid incident data
        When: POST to /api/v1/incidents
        Then: Should return 201 with created incident
        """
        # Arrange
        incident_data = {
            "title": "Ransomware Attack on Production Server",
            "description": "Critical ransomware detected encrypting files on production web server",
            "incident_type": "ransomware",
            "severity": "critical",
            "detected_at": "2026-02-06T10:00:00Z",
            "assigned_to": "security-team@example.com",
            "related_assets": ["srv-prod-01", "db-primary-02"],
        }

        # Act
        response = await async_client.post("/api/v1/incidents", json=incident_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Ransomware Attack on Production Server"
        assert data["incident_type"] == "ransomware"
        assert data["severity"] == "critical"
        assert data["status"] == "detected"  # Default status
        assert data["assigned_to"] == "security-team@example.com"
        assert "incident_number" in data
        assert data["incident_number"].startswith("INC-")
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_incident_minimal_fields(self, async_client: AsyncClient):
        """
        🔴 RED: Test incident creation with only required fields.

        Given: Incident data with only required fields
        When: POST to /api/v1/incidents
        Then: Should return 201 with optional fields as null
        """
        # Arrange
        incident_data = {
            "title": "Suspicious Login Activity",
            "description": "Multiple failed login attempts from unusual IP address",
            "incident_type": "unauthorized_access",
            "severity": "medium",
            "detected_at": "2026-02-06T10:30:00Z",
        }

        # Act
        response = await async_client.post("/api/v1/incidents", json=incident_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Suspicious Login Activity"
        assert data["status"] == "detected"
        assert data["assigned_to"] is None
        assert data["response_plan"] is None
        assert data["contained_at"] is None

    async def test_create_incident_invalid_severity(self, async_client: AsyncClient):
        """
        🔴 RED: Test validation fails for invalid severity.

        Given: Incident data with invalid severity value
        When: POST to /api/v1/incidents
        Then: Should return 422 validation error
        """
        # Arrange
        incident_data = {
            "title": "Test Incident",
            "description": "Test description for validation",
            "incident_type": "malware",
            "severity": "super_critical",  # Invalid
            "detected_at": "2026-02-06T10:00:00Z",
        }

        # Act
        response = await async_client.post("/api/v1/incidents", json=incident_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()

    async def test_create_incident_missing_required_field(self, async_client: AsyncClient):
        """
        🔴 RED: Test validation fails for missing required field.

        Given: Incident data missing title
        When: POST to /api/v1/incidents
        Then: Should return 422 validation error
        """
        # Arrange
        incident_data = {
            # Missing title
            "description": "Test description",
            "incident_type": "malware",
            "severity": "high",
            "detected_at": "2026-02-06T10:00:00Z",
        }

        # Act
        response = await async_client.post("/api/v1/incidents", json=incident_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestGetIncident:
    """Tests for GET /api/v1/incidents/{id} endpoint"""

    async def test_get_incident_by_id_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test getting incident by ID.

        Given: An existing incident
        When: GET /api/v1/incidents/{id}
        Then: Should return 200 with incident details
        """
        # Arrange - Create incident first
        incident_data = {
            "title": "Data Breach Investigation",
            "description": "Potential data breach detected in customer database",
            "incident_type": "data_breach",
            "severity": "critical",
            "detected_at": "2026-02-06T09:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        incident_id = create_response.json()["id"]

        # Act
        response = await async_client.get(f"/api/v1/incidents/{incident_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == incident_id
        assert data["title"] == "Data Breach Investigation"
        assert data["incident_type"] == "data_breach"
        assert data["severity"] == "critical"

    async def test_get_incident_not_found(self, async_client: AsyncClient):
        """
        🔴 RED: Test getting non-existent incident.

        Given: A non-existent incident ID
        When: GET /api/v1/incidents/{id}
        Then: Should return 404
        """
        # Arrange
        fake_id = str(uuid4())

        # Act
        response = await async_client.get(f"/api/v1/incidents/{fake_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()


@pytest.mark.asyncio
class TestListIncidents:
    """Tests for GET /api/v1/incidents endpoint"""

    async def test_list_incidents_no_filters(self, async_client: AsyncClient):
        """
        🔴 RED: Test listing all incidents without filters.

        Given: Multiple incidents in database
        When: GET /api/v1/incidents
        Then: Should return 200 with all incidents
        """
        # Arrange - Create 3 incidents
        incidents_data = [
            {
                "title": "Incident 1",
                "description": "Description 1 for testing",
                "incident_type": "malware",
                "severity": "critical",
                "detected_at": "2026-02-06T10:00:00Z",
            },
            {
                "title": "Incident 2",
                "description": "Description 2 for testing",
                "incident_type": "phishing",
                "severity": "high",
                "detected_at": "2026-02-06T11:00:00Z",
            },
            {
                "title": "Incident 3",
                "description": "Description 3 for testing",
                "incident_type": "dos_ddos",
                "severity": "medium",
                "detected_at": "2026-02-06T12:00:00Z",
            },
        ]
        
        for incident_data in incidents_data:
            response = await async_client.post("/api/v1/incidents", json=incident_data)
            assert response.status_code == status.HTTP_201_CREATED

        # Act
        response = await async_client.get("/api/v1/incidents")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3  # At least our 3 incidents

    async def test_list_incidents_filter_by_severity(self, async_client: AsyncClient):
        """
        🔴 RED: Test filtering incidents by severity.

        Given: Incidents with different severities
        When: GET /api/v1/incidents?severity=critical
        Then: Should return only critical incidents
        """
        # Arrange - Create incidents with different severities
        critical_incident = {
            "title": "Critical Incident",
            "description": "Critical severity incident for testing",
            "incident_type": "ransomware",
            "severity": "critical",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        medium_incident = {
            "title": "Medium Incident",
            "description": "Medium severity incident for testing",
            "incident_type": "malware",
            "severity": "medium",
            "detected_at": "2026-02-06T11:00:00Z",
        }
        
        await async_client.post("/api/v1/incidents", json=critical_incident)
        await async_client.post("/api/v1/incidents", json=medium_incident)

        # Act
        response = await async_client.get("/api/v1/incidents?severity=critical")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        for incident in data:
            assert incident["severity"] == "critical"

    async def test_list_incidents_filter_by_status(self, async_client: AsyncClient):
        """
        🔴 RED: Test filtering incidents by status.

        Given: Incidents with different statuses
        When: GET /api/v1/incidents?status=contained
        Then: Should return only contained incidents
        """
        # Arrange - Create incident and update its status
        incident_data = {
            "title": "Contained Incident",
            "description": "Incident that will be contained for testing",
            "incident_type": "malware",
            "severity": "high",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Update status to contained
        await async_client.put(
            f"/api/v1/incidents/{incident_id}/status",
            json={"status": "contained", "updated_by": "test@example.com"}
        )

        # Act
        response = await async_client.get("/api/v1/incidents?status=contained")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        for incident in data:
            assert incident["status"] == "contained"

    async def test_list_incidents_pagination(self, async_client: AsyncClient):
        """
        🔴 RED: Test pagination of incidents list.

        Given: Multiple incidents in database
        When: GET /api/v1/incidents?limit=2&offset=0
        Then: Should return paginated results
        """
        # Arrange - Create 5 incidents
        for i in range(5):
            incident_data = {
                "title": f"Incident {i+1}",
                "description": f"Description {i+1} for pagination testing",
                "incident_type": "malware",
                "severity": "medium",
                "detected_at": f"2026-02-06T{10+i}:00:00Z",
            }
            await async_client.post("/api/v1/incidents", json=incident_data)

        # Act
        response = await async_client.get("/api/v1/incidents?limit=2&offset=0")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
class TestUpdateIncident:
    """Tests for PATCH /api/v1/incidents/{id} endpoint"""

    async def test_update_incident_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test updating incident fields.

        Given: An existing incident
        When: PATCH /api/v1/incidents/{id} with updated data
        Then: Should return 200 with updated incident
        """
        # Arrange - Create incident first
        incident_data = {
            "title": "Original Title",
            "description": "Original description for testing updates",
            "incident_type": "malware",
            "severity": "medium",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]

        # Act
        update_data = {
            "title": "Updated Title",
            "severity": "high",
            "impact_assessment": "High impact on production systems",
        }
        response = await async_client.patch(
            f"/api/v1/incidents/{incident_id}",
            json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["severity"] == "high"
        assert data["impact_assessment"] == "High impact on production systems"

    async def test_update_incident_not_found(self, async_client: AsyncClient):
        """
        🔴 RED: Test updating non-existent incident.

        Given: A non-existent incident ID
        When: PATCH /api/v1/incidents/{id}
        Then: Should return 404
        """
        # Arrange
        fake_id = str(uuid4())
        update_data = {"title": "Updated Title"}

        # Act
        response = await async_client.patch(
            f"/api/v1/incidents/{fake_id}",
            json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestUpdateIncidentStatus:
    """Tests for PUT /api/v1/incidents/{id}/status endpoint"""

    async def test_update_status_to_contained(self, async_client: AsyncClient):
        """
        🔴 RED: Test updating incident status to contained.

        Given: An incident in detected status
        When: PUT /api/v1/incidents/{id}/status with status=contained
        Then: Should return 200 with contained_at timestamp set
        """
        # Arrange
        incident_data = {
            "title": "Malware Outbreak",
            "description": "Malware detected on multiple workstations",
            "incident_type": "malware",
            "severity": "high",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]

        # Act
        status_update = {
            "status": "contained",
            "updated_by": "responder@example.com"
        }
        response = await async_client.put(
            f"/api/v1/incidents/{incident_id}/status",
            json=status_update
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "contained"
        assert data["contained_at"] is not None

    async def test_update_status_to_resolved(self, async_client: AsyncClient):
        """
        🔴 RED: Test updating incident status to resolved.

        Given: An incident in contained status
        When: PUT /api/v1/incidents/{id}/status with status=resolved
        Then: Should return 200 with resolved_at timestamp set
        """
        # Arrange - Create and contain incident
        incident_data = {
            "title": "Security Breach",
            "description": "Unauthorized access to system",
            "incident_type": "unauthorized_access",
            "severity": "critical",
            "detected_at": "2026-02-06T09:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Contain first
        await async_client.put(
            f"/api/v1/incidents/{incident_id}/status",
            json={"status": "contained", "updated_by": "responder@example.com"}
        )

        # Act - Resolve
        status_update = {
            "status": "resolved",
            "updated_by": "responder@example.com"
        }
        response = await async_client.put(
            f"/api/v1/incidents/{incident_id}/status",
            json=status_update
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolved_at"] is not None
        assert data["resolution_time"] is not None


@pytest.mark.asyncio
class TestAddActionTaken:
    """Tests for POST /api/v1/incidents/{id}/actions endpoint"""

    async def test_add_action_taken_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test adding action to incident.

        Given: An existing incident
        When: POST /api/v1/incidents/{id}/actions with action data
        Then: Should return 200 with updated actions_taken list
        """
        # Arrange
        incident_data = {
            "title": "Phishing Attack",
            "description": "Phishing email campaign targeting employees",
            "incident_type": "phishing",
            "severity": "high",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]

        # Act
        action_data = {
            "timestamp": "2026-02-06T11:00:00Z",
            "action": "blocked_sender_domain",
            "description": "Blocked malicious sender domain in email gateway",
            "status": "completed",
            "performed_by": "security-team@example.com"
        }
        response = await async_client.post(
            f"/api/v1/incidents/{incident_id}/actions",
            json=action_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["actions_taken"] is not None
        assert len(data["actions_taken"]) == 1
        assert data["actions_taken"][0]["action"] == "blocked_sender_domain"


@pytest.mark.asyncio
class TestGetIncidentTimeline:
    """Tests for GET /api/v1/incidents/{id}/timeline endpoint"""

    async def test_get_timeline_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test getting incident timeline.

        Given: An incident with multiple status transitions
        When: GET /api/v1/incidents/{id}/timeline
        Then: Should return ordered timeline events
        """
        # Arrange - Create incident and transition through states
        incident_data = {
            "title": "DDoS Attack",
            "description": "Distributed denial of service attack detected",
            "incident_type": "dos_ddos",
            "severity": "critical",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        create_response = await async_client.post("/api/v1/incidents", json=incident_data)
        incident_id = create_response.json()["id"]
        
        # Transition to contained
        await async_client.put(
            f"/api/v1/incidents/{incident_id}/status",
            json={"status": "contained", "updated_by": "responder@example.com"}
        )
        
        # Add action
        await async_client.post(
            f"/api/v1/incidents/{incident_id}/actions",
            json={
                "timestamp": "2026-02-06T11:30:00Z",
                "action": "enabled_rate_limiting",
                "description": "Enabled rate limiting on load balancer",
                "status": "completed",
                "performed_by": "ops-team@example.com"
            }
        )

        # Act
        response = await async_client.get(f"/api/v1/incidents/{incident_id}/timeline")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        timeline = response.json()
        assert isinstance(timeline, list)
        assert len(timeline) >= 2  # At least detected and contained events
        
        # Verify chronological order
        timestamps = [event["timestamp"] for event in timeline]
        assert timestamps == sorted(timestamps)


@pytest.mark.asyncio
class TestGetIncidentStatistics:
    """Tests for GET /api/v1/incidents/statistics endpoint"""

    async def test_get_statistics_success(self, async_client: AsyncClient):
        """
        🔴 RED: Test getting incident statistics.

        Given: Multiple resolved incidents
        When: GET /api/v1/incidents/statistics
        Then: Should return MTTR and other metrics
        """
        # Arrange - Create and resolve incidents
        for i in range(3):
            incident_data = {
                "title": f"Test Incident {i+1}",
                "description": f"Test description {i+1} for statistics",
                "incident_type": "malware",
                "severity": "high",
                "detected_at": f"2026-02-0{i+1}T10:00:00Z",
            }
            create_response = await async_client.post("/api/v1/incidents", json=incident_data)
            incident_id = create_response.json()["id"]
            
            # Resolve incident
            await async_client.put(
                f"/api/v1/incidents/{incident_id}/status",
                json={"status": "resolved", "updated_by": "test@example.com"}
            )

        # Act
        response = await async_client.get("/api/v1/incidents/statistics")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert "mttr" in stats
        assert "total_incidents" in stats
        assert "severity_distribution" in stats
        assert stats["total_incidents"] >= 3

    async def test_get_statistics_with_date_range(self, async_client: AsyncClient):
        """
        🔴 RED: Test getting statistics with date range filter.

        Given: Incidents in different date ranges
        When: GET /api/v1/incidents/statistics?start_date=X&end_date=Y
        Then: Should return statistics for that date range only
        """
        # Arrange
        old_incident = {
            "title": "Old Incident",
            "description": "Old incident outside date range",
            "incident_type": "malware",
            "severity": "low",
            "detected_at": "2026-01-01T10:00:00Z",
        }
        recent_incident = {
            "title": "Recent Incident",
            "description": "Recent incident within date range",
            "incident_type": "phishing",
            "severity": "high",
            "detected_at": "2026-02-06T10:00:00Z",
        }
        
        await async_client.post("/api/v1/incidents", json=old_incident)
        await async_client.post("/api/v1/incidents", json=recent_incident)

        # Act
        response = await async_client.get(
            "/api/v1/incidents/statistics?start_date=2026-02-01&end_date=2026-02-28"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert "total_incidents" in stats
        # Should only count incidents in February 2026

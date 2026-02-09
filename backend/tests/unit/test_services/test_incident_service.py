"""
Unit tests for IncidentService (CRUD operations).

Siguiendo TDD (Test-Driven Development):
- 🔴 RED: Estos tests deben FALLAR primero
- 🟢 GREEN: Implementar código mínimo para pasar
- 🔵 REFACTOR: Mejorar código manteniendo tests verdes

Tests de CRUD básico:
1. Crear incidente con auto-generación de incident_number
2. Obtener incidente por ID
3. Listar incidentes con filtros
4. Actualizar estado de incidente
5. Agregar acción a incidente
6. Obtener timeline ordenado
7. Calcular estadísticas (MTTR)
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.incident_response.models.incident import Incident
from app.features.incident_response.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
)
from app.features.incident_response.services.incident_service import IncidentService
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
async def incident_service(db_session: AsyncSession) -> IncidentService:
    """Fixture que proporciona una instancia de IncidentService."""
    return IncidentService(db_session)


@pytest.fixture
async def sample_incident_data() -> IncidentCreate:
    """Fixture con datos de ejemplo para crear incidente."""
    return IncidentCreate(
        title="Ransomware Attack on Production Server",
        description="Detected ransomware encryption activity on srv-prod-01. Multiple files encrypted with .locked extension.",
        incident_type=IncidentType.RANSOMWARE,
        severity=IncidentSeverity.CRITICAL,
        detected_at=datetime.now(timezone.utc),
        assigned_to="security-team@example.com",
        related_assets=["srv-prod-01", "db-primary-02"],
    )


@pytest.fixture
async def created_incident(
    incident_service: IncidentService,
    sample_incident_data: IncidentCreate,
) -> Incident:
    """Fixture que crea y retorna un incidente en la base de datos."""
    incident = await incident_service.create(
        incident_data=sample_incident_data,
        created_by="test-user@example.com",
    )
    return incident


# ============================================================================
# TEST 1: CREATE - Auto-generación de incident_number
# ============================================================================


@pytest.mark.asyncio
async def test_create_incident_generates_incident_number(
    incident_service: IncidentService,
    sample_incident_data: IncidentCreate,
):
    """
    🔴 RED: Test que create() genera automáticamente incident_number.

    Given: Datos válidos de incidente sin incident_number
    When: Se llama a service.create()
    Then:
        - El incidente es creado exitosamente
        - incident_number es generado automáticamente con formato INC-YYYY-*
        - Todos los campos son guardados correctamente
        - created_at y updated_at son establecidos
    """
    # Act
    incident = await incident_service.create(
        incident_data=sample_incident_data,
        created_by="test-user@example.com",
    )

    # Assert
    assert incident is not None, "Incident should be created"
    assert incident.id is not None, "Incident should have UUID"
    assert incident.incident_number is not None, "Incident number should be generated"
    assert incident.incident_number.startswith("INC-"), "Incident number format should be INC-*"
    assert incident.title == sample_incident_data.title
    assert incident.description == sample_incident_data.description
    assert incident.incident_type == sample_incident_data.incident_type
    assert incident.severity == sample_incident_data.severity
    assert incident.status == IncidentStatus.DETECTED, "New incident should be in DETECTED status"
    assert incident.assigned_to == sample_incident_data.assigned_to
    assert incident.created_at is not None
    assert incident.updated_at is not None


# ============================================================================
# TEST 2: READ - Obtener por ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_incident_by_id(
    incident_service: IncidentService,
    created_incident: Incident,
):
    """
    🔴 RED: Test que get_by_id() retorna incidente correcto.

    Given: Un incidente existente en la base de datos
    When: Se llama a service.get_by_id(incident_id)
    Then:
        - El incidente correcto es retornado
        - Todos los campos están presentes
        - Retorna None si el ID no existe
    """
    # Act - Get existing incident
    incident = await incident_service.get_by_id(str(created_incident.id))

    # Assert - Found
    assert incident is not None, "Incident should be found"
    assert incident.id == created_incident.id
    assert incident.incident_number == created_incident.incident_number
    assert incident.title == created_incident.title

    # Act - Get non-existing incident
    non_existing = await incident_service.get_by_id(str(uuid4()))

    # Assert - Not found
    assert non_existing is None, "Non-existing incident should return None"


# ============================================================================
# TEST 3: READ - Listar con filtros
# ============================================================================


@pytest.mark.asyncio
async def test_list_incidents_with_severity_filter(
    incident_service: IncidentService,
    db_session: AsyncSession,
):
    """
    🔴 RED: Test que list() aplica filtros correctamente.

    Given: 3 incidentes con diferentes severidades
    When: Se llama a service.list() con filtro de severidad
    Then:
        - Solo incidentes que cumplen el filtro son retornados
        - Los resultados están ordenados por detected_at DESC
        - Limit y offset funcionan correctamente
    """
    # Arrange - Create 3 incidents with different severities
    incidents_data = [
        IncidentCreate(
            title="Critical Incident",
            description="Critical security incident",
            incident_type=IncidentType.RANSOMWARE,
            severity=IncidentSeverity.CRITICAL,
            detected_at=datetime.now(timezone.utc) - timedelta(hours=3),
        ),
        IncidentCreate(
            title="High Incident",
            description="High severity incident",
            incident_type=IncidentType.MALWARE,
            severity=IncidentSeverity.HIGH,
            detected_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        IncidentCreate(
            title="Medium Incident",
            description="Medium severity incident",
            incident_type=IncidentType.PHISHING,
            severity=IncidentSeverity.MEDIUM,
            detected_at=datetime.now(timezone.utc) - timedelta(hours=1),
        ),
    ]

    for incident_data in incidents_data:
        await incident_service.create(incident_data, "test-user@example.com")

    # Act - Filter by CRITICAL severity
    critical_incidents = await incident_service.list(
        filters={"severity": IncidentSeverity.CRITICAL},
        limit=10,
        offset=0,
    )

    # Assert - Only critical incidents
    assert len(critical_incidents) == 1, "Should return only 1 critical incident"
    assert critical_incidents[0].severity == IncidentSeverity.CRITICAL
    assert critical_incidents[0].title == "Critical Incident"

    # Act - Get all incidents
    all_incidents = await incident_service.list(
        filters={},
        limit=10,
        offset=0,
    )

    # Assert - All 3 incidents, ordered by detected_at DESC (most recent first)
    assert len(all_incidents) >= 3, "Should return at least 3 incidents"
    # Most recent (Medium) should be first
    assert all_incidents[0].title == "Medium Incident"


# ============================================================================
# TEST 4: UPDATE - Actualizar estado
# ============================================================================


@pytest.mark.asyncio
async def test_update_incident_status(
    incident_service: IncidentService,
    created_incident: Incident,
):
    """
    🔴 RED: Test que update_status() actualiza el estado correctamente.

    Given: Un incidente en estado DETECTED
    When: Se llama a service.update_status(incident_id, CONTAINED)
    Then:
        - El estado es actualizado a CONTAINED
        - contained_at timestamp es establecido automáticamente
        - updated_at es actualizado
        - Se registra quién hizo el cambio
    """
    # Arrange
    initial_status = created_incident.status
    assert initial_status == IncidentStatus.DETECTED

    # Act
    updated_incident = await incident_service.update_status(
        incident_id=str(created_incident.id),
        new_status=IncidentStatus.CONTAINED,
        updated_by="incident-responder@example.com",
    )

    # Assert
    assert updated_incident is not None, "Incident should be updated"
    assert updated_incident.status == IncidentStatus.CONTAINED
    assert updated_incident.contained_at is not None, "contained_at should be set"
    # updated_at should be equal or greater (SQLite has second precision)
    assert updated_incident.updated_at >= created_incident.updated_at


# ============================================================================
# TEST 5: UPDATE - Agregar acción
# ============================================================================


@pytest.mark.asyncio
async def test_add_action_taken_updates_json_field(
    incident_service: IncidentService,
    created_incident: Incident,
):
    """
    🔴 RED: Test que add_action_taken() actualiza el campo JSONB.

    Given: Un incidente sin acciones registradas
    When: Se llama a service.add_action_taken() con nueva acción
    Then:
        - La acción es agregada al array actions_taken
        - El campo JSONB es actualizado correctamente
        - Las acciones previas no son eliminadas (append)
        - La acción incluye timestamp y performed_by
    """
    # Arrange
    action_1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "isolated_system",
        "description": "Isolated compromised server from network",
        "status": "completed",
        "performed_by": "security-team@example.com",
    }

    action_2 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "blocked_ip",
        "description": "Blocked malicious IP at firewall",
        "status": "completed",
        "performed_by": "security-team@example.com",
    }

    # Act - Add first action
    incident = await incident_service.add_action_taken(
        incident_id=str(created_incident.id),
        action=action_1,
    )

    # Assert - First action added
    assert incident is not None
    assert incident.actions_taken is not None
    assert len(incident.actions_taken) == 1
    assert incident.actions_taken[0]["action"] == "isolated_system"

    # Act - Add second action
    incident = await incident_service.add_action_taken(
        incident_id=str(created_incident.id),
        action=action_2,
    )

    # Assert - Second action appended (not replaced)
    assert len(incident.actions_taken) == 2
    assert incident.actions_taken[0]["action"] == "isolated_system"
    assert incident.actions_taken[1]["action"] == "blocked_ip"


# ============================================================================
# TEST 6: READ - Obtener timeline ordenado
# ============================================================================


@pytest.mark.asyncio
async def test_get_timeline_returns_ordered_events(
    incident_service: IncidentService,
    created_incident: Incident,
):
    """
    🔴 RED: Test que get_timeline() retorna eventos ordenados cronológicamente.

    Given: Un incidente con múltiples eventos (detección, contención, resolución)
    When: Se llama a service.get_timeline(incident_id)
    Then:
        - Los eventos están ordenados por timestamp ASC
        - Todos los eventos importantes están incluidos
        - Cada evento tiene: timestamp, event, status, description
    """
    # Arrange - Update incident to add more timeline events
    await incident_service.update_status(
        incident_id=str(created_incident.id),
        new_status=IncidentStatus.INVESTIGATING,
        updated_by="analyst@example.com",
    )

    await incident_service.add_action_taken(
        incident_id=str(created_incident.id),
        action={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "analyzed_logs",
            "status": "completed",
        },
    )

    await incident_service.update_status(
        incident_id=str(created_incident.id),
        new_status=IncidentStatus.CONTAINED,
        updated_by="responder@example.com",
    )

    # Act
    timeline = await incident_service.get_timeline(str(created_incident.id))

    # Assert
    assert timeline is not None, "Timeline should exist"
    assert len(timeline) > 0, "Timeline should have events"

    # Check chronological order
    for i in range(len(timeline) - 1):
        assert (
            timeline[i]["timestamp"] <= timeline[i + 1]["timestamp"]
        ), "Events should be ordered chronologically"

    # Check required fields in events
    for event in timeline:
        assert "timestamp" in event
        assert "event" in event
        assert "status" in event
        assert "description" in event


# ============================================================================
# TEST 7: STATISTICS - Calcular MTTR
# ============================================================================


@pytest.mark.asyncio
async def test_get_statistics_calculates_mttr(
    incident_service: IncidentService,
    db_session: AsyncSession,
):
    """
    🔴 RED: Test que get_statistics() calcula MTTR correctamente.

    Given: 3 incidentes resueltos con diferentes tiempos de resolución
    When: Se llama a service.get_statistics(start_date, end_date)
    Then:
        - MTTR es calculado como promedio de tiempos de resolución
        - Solo incidentes resueltos son incluidos
        - Estadísticas incluyen: total_incidents, resolved_incidents, mttr_hours
        - Los cálculos son correctos
    """
    # Arrange - Create 3 resolved incidents with known resolution times
    now = datetime.now(timezone.utc)

    # Incident 1: Resolved in 2 hours
    incident_1_data = IncidentCreate(
        title="Incident 1",
        description="Resolved in 2 hours",
        incident_type=IncidentType.MALWARE,
        severity=IncidentSeverity.HIGH,
        detected_at=now - timedelta(hours=10),
    )
    incident_1 = await incident_service.create(incident_1_data, "user@example.com")
    await incident_service.update(
        str(incident_1.id),
        IncidentUpdate(
            status=IncidentStatus.CLOSED,
            resolved_at=now - timedelta(hours=8),  # 2 hours after detection
        ),
    )

    # Incident 2: Resolved in 4 hours
    incident_2_data = IncidentCreate(
        title="Incident 2",
        description="Resolved in 4 hours",
        incident_type=IncidentType.PHISHING,
        severity=IncidentSeverity.MEDIUM,
        detected_at=now - timedelta(hours=8),
    )
    incident_2 = await incident_service.create(incident_2_data, "user@example.com")
    await incident_service.update(
        str(incident_2.id),
        IncidentUpdate(
            status=IncidentStatus.CLOSED,
            resolved_at=now - timedelta(hours=4),  # 4 hours after detection
        ),
    )

    # Incident 3: Resolved in 6 hours
    incident_3_data = IncidentCreate(
        title="Incident 3",
        description="Resolved in 6 hours",
        incident_type=IncidentType.DATA_BREACH,
        severity=IncidentSeverity.CRITICAL,
        detected_at=now - timedelta(hours=7),
    )
    incident_3 = await incident_service.create(incident_3_data, "user@example.com")
    await incident_service.update(
        str(incident_3.id),
        IncidentUpdate(
            status=IncidentStatus.CLOSED,
            resolved_at=now - timedelta(hours=1),  # 6 hours after detection
        ),
    )

    # Act
    stats = await incident_service.get_statistics(
        start_date=now - timedelta(days=1),
        end_date=now,
    )

    # Assert
    assert stats is not None, "Statistics should be returned"
    assert "total_incidents" in stats
    assert "resolved_incidents" in stats
    assert "mttr_hours" in stats

    assert stats["resolved_incidents"] >= 3, "Should have at least 3 resolved incidents"
    assert stats["total_incidents"] >= 3, "Should have at least 3 total incidents"

    # MTTR should be average of 2h, 4h, 6h = 4 hours
    # (allowing some tolerance for test execution time)
    assert 3.9 <= stats["mttr_hours"] <= 4.1, f"MTTR should be ~4 hours, got {stats['mttr_hours']}"

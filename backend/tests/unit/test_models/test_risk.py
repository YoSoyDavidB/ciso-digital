"""
🔴 RED: Unit tests for Risk model - TDD Phase 1.

Tests para el nuevo schema del modelo Risk.
Estos tests deben FALLAR inicialmente porque el modelo necesita actualizarse.

Schema del modelo Risk:
- id: UUID (primary key)
- risk_number: String único (ej: RISK-2026-001)
- title: String (max 255)
- description: Text
- severity: Enum (critical, high, medium, low)
- likelihood: Enum (high, medium, low)
- impact_score: Float (0.0-10.0)
- status: Enum (open, in_progress, mitigated, accepted)
- category: Enum (technical, operational, compliance)
- assigned_to: String opcional (email)
- mitigation_plan: Text opcional
- deadline: Date opcional
- created_at: DateTime
- updated_at: DateTime
"""

from datetime import date, datetime
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError

# Este import puede fallar si el modelo necesita actualización
from app.shared.models.risk import Risk


@pytest.mark.asyncio
async def test_create_risk_with_required_fields(db_session):
    """
    🔴 RED: Test que Risk se crea con campos requeridos.

    Given: Datos mínimos requeridos para un Risk
    When: Se crea una instancia de Risk
    Then: El modelo debe tener todos los campos correctos
    """
    # Arrange
    risk_data = {
        "risk_number": "RISK-2026-001",
        "title": "SQL Injection Vulnerability",
        "description": "Critical SQL injection found in login endpoint",
        "severity": "critical",
        "likelihood": "high",
        "impact_score": 9.5,
        "status": "open",
        "category": "technical",
    }

    # Act
    risk = Risk(**risk_data)
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Assert
    assert risk.id is not None
    assert isinstance(risk.id, UUID)
    assert risk.risk_number == "RISK-2026-001"
    assert risk.title == "SQL Injection Vulnerability"
    assert risk.description == "Critical SQL injection found in login endpoint"
    assert risk.severity == "critical"
    assert risk.likelihood == "high"
    assert risk.impact_score == 9.5
    assert risk.status == "open"
    assert risk.category == "technical"
    assert risk.assigned_to is None  # Campo opcional
    assert risk.mitigation_plan is None  # Campo opcional
    assert risk.deadline is None  # Campo opcional


@pytest.mark.asyncio
async def test_risk_severity_enum_validation(db_session):
    """
    🔴 RED: Test que severity solo acepta valores válidos del enum.

    Given: Risk con severity válida e inválida
    When: Se intenta guardar
    Then: Debe aceptar valores válidos y rechazar inválidos
    """
    # Test valores válidos
    valid_severities = ["critical", "high", "medium", "low"]

    for idx, severity in enumerate(valid_severities, start=1):
        risk = Risk(
            risk_number=f"RISK-2026-SEV-{idx:03d}",
            title=f"Risk with {severity} severity",
            description="Test description",
            severity=severity,
            likelihood="medium",
            impact_score=5.0,
            status="open",
            category="technical",
        )
        db_session.add(risk)
        await db_session.commit()
        await db_session.refresh(risk)

        # Assert
        assert risk.severity == severity

    # Test valor inválido - debe fallar en validación
    with pytest.raises((ValueError, IntegrityError)):
        risk_invalid = Risk(
            risk_number="RISK-2026-SEV-INVALID",
            title="Invalid severity",
            description="Should fail",
            severity="extreme",  # Valor inválido
            likelihood="high",
            impact_score=8.0,
            status="open",
            category="technical",
        )
        db_session.add(risk_invalid)
        await db_session.commit()


@pytest.mark.asyncio
async def test_risk_status_enum_validation(db_session):
    """
    🔴 RED: Test que status solo acepta valores válidos del enum.

    Given: Risk con diferentes status
    When: Se intenta guardar
    Then: Debe aceptar valores válidos: open, in_progress, mitigated, accepted
    """
    # Test valores válidos
    valid_statuses = ["open", "in_progress", "mitigated", "accepted"]

    for idx, status in enumerate(valid_statuses, start=1):
        risk = Risk(
            risk_number=f"RISK-2026-STA-{idx:03d}",
            title=f"Risk with {status} status",
            description="Test description",
            severity="medium",
            likelihood="low",
            impact_score=4.0,
            status=status,
            category="operational",
        )
        db_session.add(risk)
        await db_session.commit()
        await db_session.refresh(risk)

        # Assert
        assert risk.status == status

    # Test valor inválido
    with pytest.raises((ValueError, IntegrityError)):
        risk_invalid = Risk(
            risk_number="RISK-2026-STA-INVALID",
            title="Invalid status",
            description="Should fail",
            severity="low",
            likelihood="low",
            impact_score=2.0,
            status="archived",  # Valor inválido
            category="compliance",
        )
        db_session.add(risk_invalid)
        await db_session.commit()


# =============================================================================
# 🔴 RED: Tests for Refactored Features (5.3)
# =============================================================================


@pytest.mark.asyncio
async def test_risk_create_classmethod_generates_risk_number(db_session):
    """
    🔴 RED: Test que Risk.create() auto-genera risk_number.

    Given: Datos de risk sin risk_number
    When: Se llama a Risk.create()
    Then: Debe generar automáticamente risk_number con formato RISK-YYYY-NNN
    """
    # Arrange
    risk_data = {
        "title": "Auto-generated Risk Number",
        "description": "Testing auto-generation of risk_number",
        "severity": "high",
        "likelihood": "medium",
        "impact_score": 7.0,
        "category": "technical",
    }

    # Act
    risk = await Risk.create(db_session, **risk_data)

    # Assert
    assert risk.risk_number is not None
    assert risk.risk_number.startswith("RISK-2026-")
    assert len(risk.risk_number.split("-")) == 3
    assert risk.risk_number.split("-")[2].isdigit()
    assert risk.title == "Auto-generated Risk Number"
    assert risk.status == "open"  # Default status


@pytest.mark.asyncio
async def test_risk_create_increments_number_sequence(db_session):
    """
    🔴 RED: Test que Risk.create() incrementa el número secuencial.

    Given: Múltiples llamadas a Risk.create()
    When: Se crean varios riesgos
    Then: Los números deben incrementar: 001, 002, 003, etc.
    """
    # Act - Crear 3 riesgos
    risks = []
    for i in range(3):
        risk = await Risk.create(
            db_session,
            title=f"Sequential Risk {i+1}",
            description=f"Risk number {i+1}",
            severity="low",
            likelihood="low",
            impact_score=2.0,
            category="operational",
        )
        risks.append(risk)

    # Assert
    risk_numbers = [r.risk_number for r in risks]
    assert len(risk_numbers) == 3
    assert len(set(risk_numbers)) == 3  # Todos únicos

    # Extraer números secuenciales
    sequences = [int(rn.split("-")[2]) for rn in risk_numbers]
    assert sequences[0] < sequences[1] < sequences[2]  # Incrementales


@pytest.mark.asyncio
async def test_risk_create_accepts_custom_risk_number(db_session):
    """
    🔴 RED: Test que Risk.create() permite especificar risk_number custom.

    Given: risk_number específico en los datos
    When: Se llama a Risk.create()
    Then: Debe usar el risk_number proporcionado en lugar de generarlo
    """
    # Arrange
    custom_number = "RISK-CUSTOM-999"

    # Act
    risk = await Risk.create(
        db_session,
        risk_number=custom_number,
        title="Custom Risk Number",
        description="Testing custom risk_number",
        severity="medium",
        likelihood="medium",
        impact_score=5.0,
        category="compliance",
    )

    # Assert
    assert risk.risk_number == custom_number


@pytest.mark.asyncio
async def test_calculated_risk_score_property(db_session):
    """
    🔴 RED: Test que calculated_risk_score calcula correctamente.

    Given: Risk con likelihood e impact_score conocidos
    When: Se accede a calculated_risk_score property
    Then: Debe calcular score = (likelihood_weight * impact_score)

    Fórmula:
    - high likelihood = 1.0
    - medium likelihood = 0.6
    - low likelihood = 0.3
    - calculated_risk_score = likelihood_weight * impact_score
    """
    # Test High Likelihood
    risk_high = Risk(
        risk_number="RISK-2026-CALC-001",
        title="High Likelihood Risk",
        description="Testing calculated score",
        severity="critical",
        likelihood="high",  # weight = 1.0
        impact_score=10.0,
        status="open",
        category="technical",
    )
    db_session.add(risk_high)
    await db_session.commit()
    await db_session.refresh(risk_high)

    assert risk_high.calculated_risk_score == 10.0  # 1.0 * 10.0

    # Test Medium Likelihood
    risk_medium = Risk(
        risk_number="RISK-2026-CALC-002",
        title="Medium Likelihood Risk",
        description="Testing calculated score",
        severity="high",
        likelihood="medium",  # weight = 0.6
        impact_score=10.0,
        status="open",
        category="technical",
    )
    db_session.add(risk_medium)
    await db_session.commit()
    await db_session.refresh(risk_medium)

    assert risk_medium.calculated_risk_score == 6.0  # 0.6 * 10.0

    # Test Low Likelihood
    risk_low = Risk(
        risk_number="RISK-2026-CALC-003",
        title="Low Likelihood Risk",
        description="Testing calculated score",
        severity="medium",
        likelihood="low",  # weight = 0.3
        impact_score=10.0,
        status="open",
        category="technical",
    )
    db_session.add(risk_low)
    await db_session.commit()
    await db_session.refresh(risk_low)

    assert risk_low.calculated_risk_score == 3.0  # 0.3 * 10.0


@pytest.mark.asyncio
async def test_is_overdue_returns_true_when_past_deadline(db_session):
    """
    🔴 RED: Test que is_overdue() retorna True si deadline pasó.

    Given: Risk con deadline en el pasado y status no mitigated/accepted
    When: Se llama a is_overdue()
    Then: Debe retornar True
    """
    # Arrange - Deadline en el pasado
    past_date = date(2020, 1, 1)

    risk = Risk(
        risk_number="RISK-2026-OVERDUE-001",
        title="Overdue Risk",
        description="This risk is past its deadline",
        severity="high",
        likelihood="high",
        impact_score=8.0,
        status="open",  # No mitigado
        category="technical",
        deadline=past_date,
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Act & Assert
    assert risk.is_overdue() is True


@pytest.mark.asyncio
async def test_is_overdue_returns_false_when_future_deadline(db_session):
    """
    🔴 RED: Test que is_overdue() retorna False si deadline está en el futuro.

    Given: Risk con deadline futuro
    When: Se llama a is_overdue()
    Then: Debe retornar False
    """
    # Arrange - Deadline en el futuro
    future_date = date(2030, 12, 31)

    risk = Risk(
        risk_number="RISK-2026-FUTURE-001",
        title="Future Deadline Risk",
        description="This risk has future deadline",
        severity="medium",
        likelihood="medium",
        impact_score=5.0,
        status="open",
        category="operational",
        deadline=future_date,
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Act & Assert
    assert risk.is_overdue() is False


@pytest.mark.asyncio
async def test_is_overdue_returns_false_when_no_deadline(db_session):
    """
    🔴 RED: Test que is_overdue() retorna False si no hay deadline.

    Given: Risk sin deadline
    When: Se llama a is_overdue()
    Then: Debe retornar False
    """
    # Arrange - Sin deadline
    risk = Risk(
        risk_number="RISK-2026-NODATE-001",
        title="No Deadline Risk",
        description="This risk has no deadline",
        severity="low",
        likelihood="low",
        impact_score=2.0,
        status="open",
        category="compliance",
        deadline=None,  # Sin deadline
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Act & Assert
    assert risk.is_overdue() is False


@pytest.mark.asyncio
async def test_is_overdue_returns_false_when_mitigated(db_session):
    """
    🔴 RED: Test que is_overdue() retorna False si risk está mitigated.

    Given: Risk con deadline pasado pero status=mitigated
    When: Se llama a is_overdue()
    Then: Debe retornar False (porque ya fue mitigado)
    """
    # Arrange - Deadline pasado pero mitigado
    past_date = date(2020, 1, 1)

    risk = Risk(
        risk_number="RISK-2026-MITIGATED-001",
        title="Mitigated Risk",
        description="This risk was mitigated",
        severity="high",
        likelihood="high",
        impact_score=8.0,
        status="mitigated",  # Ya mitigado
        category="technical",
        deadline=past_date,
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Act & Assert
    assert risk.is_overdue() is False


@pytest.mark.asyncio
async def test_is_overdue_returns_false_when_accepted(db_session):
    """
    🔴 RED: Test que is_overdue() retorna False si risk está accepted.

    Given: Risk con deadline pasado pero status=accepted
    When: Se llama a is_overdue()
    Then: Debe retornar False (porque fue aceptado el riesgo)
    """
    # Arrange - Deadline pasado pero aceptado
    past_date = date(2020, 1, 1)

    risk = Risk(
        risk_number="RISK-2026-ACCEPTED-001",
        title="Accepted Risk",
        description="This risk was accepted",
        severity="low",
        likelihood="low",
        impact_score=2.0,
        status="accepted",  # Aceptado
        category="operational",
        deadline=past_date,
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Act & Assert
    assert risk.is_overdue() is False


@pytest.mark.asyncio
async def test_risk_number_is_unique(db_session):
    """
    🔴 RED: Test que risk_number debe ser único.

    Given: Dos Risks con el mismo risk_number
    When: Se intenta guardar el segundo
    Then: Debe lanzar IntegrityError por violación de unique constraint
    """
    # Arrange
    risk1 = Risk(
        risk_number="RISK-2026-DUP-001",
        title="First Risk",
        description="First risk description",
        severity="high",
        likelihood="medium",
        impact_score=7.0,
        status="open",
        category="technical",
    )

    risk2 = Risk(
        risk_number="RISK-2026-DUP-001",  # MISMO risk_number!
        title="Second Risk",
        description="Second risk description",
        severity="medium",
        likelihood="low",
        impact_score=5.0,
        status="open",
        category="operational",
    )

    # Act & Assert
    db_session.add(risk1)
    await db_session.commit()

    # Intentar agregar el segundo con mismo risk_number debe fallar
    db_session.add(risk2)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_impact_score_within_range(db_session):
    """
    🔴 RED: Test que impact_score debe estar en rango 0.0-10.0.

    Given: Risk con impact_score válido e inválido
    When: Se intenta guardar
    Then: Debe aceptar 0.0-10.0 y rechazar fuera de rango
    """
    # Test valores válidos en los extremos
    valid_scores = [0.0, 5.0, 10.0]

    for idx, score in enumerate(valid_scores, start=1):
        risk = Risk(
            risk_number=f"RISK-2026-IMP-{idx:03d}",
            title=f"Risk with score {score}",
            description="Test description",
            severity="medium",
            likelihood="medium",
            impact_score=score,
            status="open",
            category="technical",
        )
        db_session.add(risk)
        await db_session.commit()
        await db_session.refresh(risk)

        # Assert
        assert risk.impact_score == score

    # Test valor fuera de rango (mayor a 10.0)
    with pytest.raises((ValueError, IntegrityError)):
        risk_high = Risk(
            risk_number="RISK-2026-IMP-HIGH",
            title="Invalid high score",
            description="Should fail",
            severity="critical",
            likelihood="high",
            impact_score=15.0,  # Fuera de rango
            status="open",
            category="technical",
        )
        db_session.add(risk_high)
        await db_session.commit()

    # Rollback para siguiente test
    await db_session.rollback()

    # Test valor negativo
    with pytest.raises((ValueError, IntegrityError)):
        risk_negative = Risk(
            risk_number="RISK-2026-IMP-NEG",
            title="Invalid negative score",
            description="Should fail",
            severity="low",
            likelihood="low",
            impact_score=-1.0,  # Negativo
            status="open",
            category="compliance",
        )
        db_session.add(risk_negative)
        await db_session.commit()


@pytest.mark.asyncio
async def test_timestamps_auto_populated(db_session):
    """
    🔴 RED: Test que created_at y updated_at se poblan automáticamente.

    Given: Un nuevo Risk sin especificar timestamps
    When: Se guarda en la base de datos
    Then: created_at y updated_at deben poblarse automáticamente
    """
    # Arrange
    risk = Risk(
        risk_number="RISK-2026-TS-001",
        title="Test Timestamps",
        description="Testing auto timestamps",
        severity="low",
        likelihood="low",
        impact_score=2.0,
        status="open",
        category="operational",
    )

    # Act
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Assert
    assert risk.created_at is not None
    assert risk.updated_at is not None
    assert isinstance(risk.created_at, datetime)
    assert isinstance(risk.updated_at, datetime)

    # created_at y updated_at deben ser muy cercanos (mismo momento)
    time_diff = (risk.updated_at - risk.created_at).total_seconds()
    assert time_diff < 1  # Menos de 1 segundo de diferencia


@pytest.mark.asyncio
async def test_risk_with_optional_fields(db_session):
    """
    🔴 RED: Test que campos opcionales funcionan correctamente.

    Given: Risk con todos los campos opcionales poblados
    When: Se guarda en la base de datos
    Then: Debe guardar correctamente assigned_to, mitigation_plan, deadline
    """
    # Arrange
    test_deadline = date(2026, 12, 31)

    risk = Risk(
        risk_number="RISK-2026-OPT-001",
        title="Risk with Optional Fields",
        description="Testing all optional fields",
        severity="high",
        likelihood="medium",
        impact_score=7.5,
        status="in_progress",
        category="compliance",
        assigned_to="security@company.com",
        mitigation_plan="1. Patch server\n2. Update firewall rules\n3. Monitor logs",
        deadline=test_deadline,
    )

    # Act
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # Assert
    assert risk.assigned_to == "security@company.com"
    assert risk.mitigation_plan == "1. Patch server\n2. Update firewall rules\n3. Monitor logs"
    assert risk.deadline == test_deadline
    assert isinstance(risk.deadline, date)


@pytest.mark.asyncio
async def test_risk_category_enum_validation(db_session):
    """
    🔴 RED: Test que category solo acepta valores válidos del enum.

    Given: Risk con diferentes categorías
    When: Se intenta guardar
    Then: Debe aceptar: technical, operational, compliance
    """
    # Test valores válidos
    valid_categories = ["technical", "operational", "compliance"]

    for idx, category in enumerate(valid_categories, start=1):
        risk = Risk(
            risk_number=f"RISK-2026-CAT-{idx:03d}",
            title=f"Risk in {category} category",
            description="Test description",
            severity="medium",
            likelihood="medium",
            impact_score=5.0,
            status="open",
            category=category,
        )
        db_session.add(risk)
        await db_session.commit()
        await db_session.refresh(risk)

        # Assert
        assert risk.category == category

    # Test valor inválido
    with pytest.raises((ValueError, IntegrityError)):
        risk_invalid = Risk(
            risk_number="RISK-2026-CAT-INVALID",
            title="Invalid category",
            description="Should fail",
            severity="low",
            likelihood="low",
            impact_score=3.0,
            status="open",
            category="financial",  # Valor inválido
        )
        db_session.add(risk_invalid)
        await db_session.commit()


@pytest.mark.asyncio
async def test_risk_likelihood_enum_validation(db_session):
    """
    🔴 RED: Test que likelihood solo acepta valores válidos del enum.

    Given: Risk con diferentes likelihood
    When: Se intenta guardar
    Then: Debe aceptar: high, medium, low
    """
    # Test valores válidos
    valid_likelihoods = ["high", "medium", "low"]

    for idx, likelihood in enumerate(valid_likelihoods, start=1):
        risk = Risk(
            risk_number=f"RISK-2026-LIK-{idx:03d}",
            title=f"Risk with {likelihood} likelihood",
            description="Test description",
            severity="medium",
            likelihood=likelihood,
            impact_score=5.0,
            status="open",
            category="technical",
        )
        db_session.add(risk)
        await db_session.commit()
        await db_session.refresh(risk)

        # Assert
        assert risk.likelihood == likelihood

    # Test valor inválido
    with pytest.raises((ValueError, IntegrityError)):
        risk_invalid = Risk(
            risk_number="RISK-2026-LIK-INVALID",
            title="Invalid likelihood",
            description="Should fail",
            severity="low",
            likelihood="certain",  # Valor inválido
            impact_score=3.0,
            status="open",
            category="operational",
        )
        db_session.add(risk_invalid)
        await db_session.commit()

"""
Incident Response Database Model.

Este módulo define el modelo SQLAlchemy para gestión de incidentes de seguridad,
siguiendo el framework NIST SP 800-61r2 (Computer Security Incident Handling Guide).

El modelo soporta:
- Ciclo de vida completo del incidente (detección → resolución)
- Seguimiento de SLA y métricas (MTTR, MTTD, etc.)
- Almacenamiento de evidencia y acciones ejecutadas
- Análisis de impacto y causa raíz
- Reconstrucción de timeline
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, Index, JSON, String, Text, event
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models.base import Base, TimestampMixin, UUIDMixin
from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


class Incident(Base, UUIDMixin, TimestampMixin):
    """
    Modelo de base de datos para incidentes de seguridad.

    Representa un incidente de seguridad desde su detección hasta su cierre,
    incluyendo toda la información necesaria para respuesta, análisis y
    reporte de cumplimiento.

    Attributes:
        id: UUID único del incidente (primary key)
        incident_number: Número de incidente único (e.g., "INC-2026-001")
        title: Título descriptivo del incidente
        description: Descripción detallada del incidente
        incident_type: Tipo de incidente (malware, phishing, etc.)
        severity: Nivel de severidad (critical, high, medium, low)
        status: Estado actual del incidente en su ciclo de vida
        detected_at: Timestamp de detección inicial
        reported_at: Timestamp de reporte formal
        contained_at: Timestamp de contención (opcional)
        resolved_at: Timestamp de resolución completa (opcional)
        assigned_to: Email del usuario asignado (opcional)
        response_plan: Plan de respuesta estructurado (JSON)
        actions_taken: Lista de acciones ejecutadas (JSON)
        evidence: Evidencia recolectada (JSON)
        impact_assessment: Evaluación de impacto (texto)
        root_cause: Análisis de causa raíz (texto)
        lessons_learned: Lecciones aprendidas (texto)
        related_assets: IDs de assets afectados (JSON)
        created_at: Timestamp de creación del registro
        updated_at: Timestamp de última actualización

    Example:
        >>> incident = Incident(
        ...     incident_number="INC-2026-001",
        ...     title="Ransomware Attack on Production Server",
        ...     description="Detected ransomware encryption activity...",
        ...     incident_type=IncidentType.RANSOMWARE,
        ...     severity=IncidentSeverity.CRITICAL,
        ...     status=IncidentStatus.DETECTED,
        ...     detected_at=datetime.now(timezone.utc),
        ...     reported_at=datetime.now(timezone.utc)
        ... )
        >>> db.add(incident)
        >>> await db.commit()
    """

    __tablename__ = "incidents"

    # ========================================================================
    # Core Identification Fields
    # ========================================================================

    incident_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique incident identifier (e.g., INC-2026-001)",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Short descriptive title of the incident",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of the incident",
    )

    # ========================================================================
    # Classification Fields
    # ========================================================================

    incident_type: Mapped[IncidentType] = mapped_column(
        ENUM(IncidentType, name="incident_type_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Type of security incident (malware, phishing, etc.)",
    )

    severity: Mapped[IncidentSeverity] = mapped_column(
        ENUM(IncidentSeverity, name="incident_severity_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Severity level (critical, high, medium, low)",
    )

    status: Mapped[IncidentStatus] = mapped_column(
        ENUM(IncidentStatus, name="incident_status_enum", create_type=True),
        nullable=False,
        default=IncidentStatus.DETECTED,
        index=True,
        comment="Current status in incident lifecycle",
    )

    # ========================================================================
    # Timestamp Fields (Incident Lifecycle)
    # ========================================================================

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the incident was first detected",
    )

    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="When the incident was formally reported",
    )

    contained_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the incident was contained",
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the incident was fully resolved",
    )

    # ========================================================================
    # Assignment and Ownership
    # ========================================================================

    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Email of assigned incident responder",
    )

    # ========================================================================
    # Structured Data Fields (JSON for database compatibility)
    # ========================================================================

    response_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Structured response plan steps",
    )

    actions_taken: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="List of executed response actions",
    )

    evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Collected evidence (logs, screenshots, etc.)",
    )

    related_assets: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="List of affected asset IDs",
    )

    # ========================================================================
    # Analysis and Documentation Fields
    # ========================================================================

    impact_assessment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Assessment of incident impact on business",
    )

    root_cause: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Root cause analysis findings",
    )

    lessons_learned: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Lessons learned for future prevention",
    )

    # ========================================================================
    # Indexes for Performance
    # ========================================================================

    __table_args__ = (
        Index(
            "ix_incidents_severity_status",
            "severity",
            "status",
            postgresql_where="status != 'closed'",
        ),
        Index(
            "ix_incidents_detected_at_desc",
            "detected_at",
            postgresql_ops={"detected_at": "DESC"},
        ),
        Index(
            "ix_incidents_type_severity",
            "incident_type",
            "severity",
        ),
    )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def calculate_resolution_time(self) -> Optional[timedelta]:
        """
        Calcula el tiempo total desde detección hasta resolución.

        Este es el MTTR (Mean Time To Resolve) para el incidente individual.

        Returns:
            timedelta: Tiempo de resolución, o None si no está resuelto

        Example:
            >>> incident.resolved_at = datetime(2026, 2, 6, 14, 0, 0, tzinfo=timezone.utc)
            >>> incident.detected_at = datetime(2026, 2, 6, 10, 0, 0, tzinfo=timezone.utc)
            >>> resolution_time = incident.calculate_resolution_time()
            >>> print(f"Resolved in {resolution_time.total_seconds() / 3600} hours")
            Resolved in 4.0 hours
        """
        if self.detected_at and self.resolved_at:
            return self.resolved_at - self.detected_at
        return None

    def is_sla_breached(self, sla_hours_by_severity: Dict[str, int]) -> bool:
        """
        Verifica si el incidente ha incumplido el SLA basado en severidad.

        Los SLAs típicos son:
        - CRITICAL: 1 hora
        - HIGH: 4 horas
        - MEDIUM: 24 horas
        - LOW: 72 horas

        Args:
            sla_hours_by_severity: Diccionario de horas SLA por severidad
                Ejemplo: {"critical": 1, "high": 4, "medium": 24, "low": 72}

        Returns:
            bool: True si el SLA fue incumplido, False en caso contrario

        Example:
            >>> sla_config = {
            ...     "critical": 1,
            ...     "high": 4,
            ...     "medium": 24,
            ...     "low": 72
            ... }
            >>> incident.severity = IncidentSeverity.CRITICAL
            >>> incident.detected_at = datetime.now(timezone.utc) - timedelta(hours=2)
            >>> incident.is_sla_breached(sla_config)
            True  # 2 horas > 1 hora SLA para CRITICAL
        """
        if not self.detected_at:
            return False

        # Si ya está resuelto, verificar contra tiempo de resolución
        if self.resolved_at:
            elapsed = self.resolved_at - self.detected_at
        else:
            # Si no está resuelto, verificar contra tiempo actual
            elapsed = datetime.now(timezone.utc) - self.detected_at

        # Obtener SLA para la severidad actual
        sla_hours = sla_hours_by_severity.get(self.severity.value, 24)
        sla_threshold = timedelta(hours=sla_hours)

        return elapsed > sla_threshold

    def get_timeline(self) -> List[Dict[str, Any]]:
        """
        Genera una línea de tiempo cronológica de eventos del incidente.

        Útil para reportes y análisis post-mortem.

        Returns:
            List[Dict[str, Any]]: Lista de eventos ordenados cronológicamente
                Cada evento tiene: timestamp, event, status

        Example:
            >>> timeline = incident.get_timeline()
            >>> for event in timeline:
            ...     print(f"{event['timestamp']}: {event['event']}")
            2026-02-06 10:00:00+00:00: Incident Detected
            2026-02-06 10:05:00+00:00: Incident Reported
            2026-02-06 12:00:00+00:00: Incident Contained
            2026-02-06 14:00:00+00:00: Incident Resolved
        """
        def normalize_timestamp(ts: datetime) -> datetime:
            """Ensure timestamp is timezone-aware for consistent comparison."""
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts

        timeline: List[Dict[str, Any]] = []

        if self.detected_at:
            timeline.append(
                {
                    "timestamp": normalize_timestamp(self.detected_at),
                    "event": "Incident Detected",
                    "status": IncidentStatus.DETECTED.value,
                    "description": "Initial detection of security incident",
                }
            )

        if self.reported_at and self.reported_at != self.detected_at:
            timeline.append(
                {
                    "timestamp": normalize_timestamp(self.reported_at),
                    "event": "Incident Reported",
                    "status": self.status.value,
                    "description": "Formal incident report created",
                }
            )

        if self.contained_at:
            timeline.append(
                {
                    "timestamp": normalize_timestamp(self.contained_at),
                    "event": "Incident Contained",
                    "status": IncidentStatus.CONTAINED.value,
                    "description": "Threat contained, spread limited",
                }
            )

        if self.resolved_at:
            timeline.append(
                {
                    "timestamp": normalize_timestamp(self.resolved_at),
                    "event": "Incident Resolved",
                    "status": IncidentStatus.CLOSED.value,
                    "description": "Incident fully resolved and closed",
                }
            )

        # Agregar acciones tomadas si existen
        if self.actions_taken:
            for action in self.actions_taken:
                if "timestamp" in action:
                    # Parse timestamp if it's a string
                    timestamp = action["timestamp"]
                    if isinstance(timestamp, str):
                        from dateutil import parser
                        timestamp = parser.parse(timestamp)
                    
                    # Normalize to timezone-aware
                    timestamp = normalize_timestamp(timestamp)
                    
                    timeline.append(
                        {
                            "timestamp": timestamp,
                            "event": f"Action: {action.get('action', 'Unknown')}",
                            "status": action.get("status", "in_progress"),
                            "description": action.get("description", ""),
                        }
                    )

        # Ordenar por timestamp (todos son datetime timezone-aware ahora)
        return sorted(timeline, key=lambda x: x["timestamp"])

    def __repr__(self) -> str:
        """Representación string del incidente."""
        return (
            f"<Incident("
            f"number='{self.incident_number}', "
            f"type={self.incident_type.value}, "
            f"severity={self.severity.value}, "
            f"status={self.status.value}"
            f")>"
        )


# ============================================================================
# Database Validation Events
# ============================================================================


@event.listens_for(Incident, "before_insert")
@event.listens_for(Incident, "before_update")
def validate_incident_dates(mapper, connection, target: Incident) -> None:
    """
    Valida las fechas del incidente antes de insertar o actualizar.

    Reglas de validación:
    1. detected_at debe ser <= reported_at
    2. contained_at debe ser >= detected_at (si existe)
    3. resolved_at debe ser >= contained_at (si ambos existen)

    Raises:
        ValueError: Si alguna validación falla
    """
    # Validar detected_at <= reported_at
    if target.detected_at and target.reported_at:
        if target.detected_at > target.reported_at:
            raise ValueError(
                f"detected_at ({target.detected_at}) must be earlier than or equal to "
                f"reported_at ({target.reported_at})"
            )

    # Validar contained_at >= detected_at
    if target.contained_at and target.detected_at:
        # Normalize both to timezone-aware for comparison
        contained = target.contained_at.replace(tzinfo=timezone.utc) if target.contained_at.tzinfo is None else target.contained_at
        detected = target.detected_at.replace(tzinfo=timezone.utc) if target.detected_at.tzinfo is None else target.detected_at
        
        if contained < detected:
            raise ValueError(
                f"contained_at ({target.contained_at}) must be later than or equal to "
                f"detected_at ({target.detected_at})"
            )

    # Validar resolved_at >= contained_at
    if target.resolved_at and target.contained_at:
        # Normalize both to timezone-aware for comparison
        resolved = target.resolved_at.replace(tzinfo=timezone.utc) if target.resolved_at.tzinfo is None else target.resolved_at
        contained = target.contained_at.replace(tzinfo=timezone.utc) if target.contained_at.tzinfo is None else target.contained_at
        
        if resolved < contained:
            raise ValueError(
                f"resolved_at ({target.resolved_at}) must be later than or equal to "
                f"contained_at ({target.contained_at})"
            )


@event.listens_for(Incident, "before_insert")
def generate_incident_number(mapper, connection, target: Incident) -> None:
    """
    Genera automáticamente un incident_number si no se proporciona.

    Formato: INC-YYYY-NNN
    Ejemplo: INC-2026-001

    Note:
        En producción, esto debería usar una secuencia de base de datos
        para garantizar unicidad bajo alta concurrencia.
    """
    if not target.incident_number:
        year = datetime.now(timezone.utc).year
        # En producción, usar una secuencia o contador atómico
        # Por ahora, usar timestamp con microsegundos para unicidad en tests
        now = datetime.now(timezone.utc)
        timestamp_suffix = now.strftime("%m%d%H%M%S") + f"{now.microsecond:06d}"
        target.incident_number = f"INC-{year}-{timestamp_suffix}"

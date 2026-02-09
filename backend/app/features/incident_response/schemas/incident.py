"""
Pydantic Schemas for Incident Response.

Este módulo define los schemas de validación y serialización para la API
de gestión de incidentes de seguridad.

Los schemas siguen el patrón:
- Base: Campos compartidos
- Create: Campos requeridos para creación
- Update: Campos opcionales para actualización
- Response: Campos de salida incluyendo computed fields
- Summary: Vista resumida para listados
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.shared.models.enums import IncidentSeverity, IncidentStatus, IncidentType


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class SecurityEventBase(BaseModel):
    """
    Schema base para eventos de seguridad que disparan respuesta a incidentes.

    Representa el evento inicial detectado por sistemas de monitoreo,
    SIEM, EDR, o reportado manualmente.

    Attributes:
        timestamp: Momento en que ocurrió el evento
        source: Sistema o herramienta que detectó el evento (e.g., "Splunk", "CrowdStrike")
        event_type: Tipo de evento (e.g., "malware_detection", "suspicious_login")
        description: Descripción detallada del evento
        raw_data: Datos crudos del evento original (JSON flexible)
        severity_indicator: Indicador inicial de severidad del evento
        affected_assets: Lista de assets afectados identificados

    Example:
        >>> event = SecurityEventBase(
        ...     timestamp=datetime.now(timezone.utc),
        ...     source="CrowdStrike EDR",
        ...     event_type="ransomware_detection",
        ...     description="Suspicious file encryption activity detected",
        ...     raw_data={"alert_id": "ALT-12345", "host": "srv-prod-01"},
        ...     severity_indicator="critical",
        ...     affected_assets=["srv-prod-01"]
        ... )
    """

    timestamp: datetime = Field(
        ...,
        description="Timestamp del evento de seguridad",
        examples=["2026-02-06T10:30:00Z"],
    )
    source: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sistema o herramienta que detectó el evento",
        examples=["Splunk SIEM", "CrowdStrike EDR", "AWS GuardDuty"],
    )
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tipo de evento de seguridad",
        examples=[
            "malware_detection",
            "suspicious_login",
            "data_exfiltration",
            "ransomware_activity",
        ],
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Descripción detallada del evento",
        examples=["Multiple failed login attempts from unusual IP address"],
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Datos crudos del evento original en formato JSON",
        examples=[{"alert_id": "ALT-12345", "severity": 9, "confidence": 0.95}],
    )
    severity_indicator: str = Field(
        default="medium",
        description="Indicador inicial de severidad",
        examples=["critical", "high", "medium", "low"],
    )
    affected_assets: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de assets afectados",
        examples=[["srv-prod-01", "db-primary-02"]],
    )


class IncidentBase(BaseModel):
    """
    Schema base para incidentes con campos comunes.

    Campos compartidos entre IncidentCreate y IncidentUpdate.

    Attributes:
        title: Título descriptivo del incidente
        description: Descripción detallada del incidente
        incident_type: Tipo de incidente (enum)
        severity: Nivel de severidad (enum)
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Título descriptivo del incidente",
        examples=["Ransomware Attack on Production Server"],
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Descripción detallada del incidente",
        examples=[
            "Detected ransomware encryption activity on production web server. "
            "Multiple files encrypted with .locked extension. Server isolated from network."
        ],
    )
    incident_type: IncidentType = Field(
        ...,
        description="Tipo de incidente de seguridad",
        examples=["ransomware"],
    )
    severity: IncidentSeverity = Field(
        ...,
        description="Nivel de severidad del incidente",
        examples=["critical"],
    )


# ============================================================================
# CREATE SCHEMA
# ============================================================================


class IncidentCreate(IncidentBase):
    """
    Schema para crear un nuevo incidente.

    Extiende IncidentBase con campos requeridos para la creación inicial.

    Attributes:
        detected_at: Timestamp de detección del incidente
        reported_at: Timestamp de reporte formal (opcional, por defecto = detected_at)
        assigned_to: Email del usuario asignado (opcional)
        related_assets: Lista de IDs de assets afectados
        response_plan: Plan de respuesta inicial (opcional)
        evidence: Evidencia inicial recolectada (opcional)

    Validations:
        - title debe tener entre 5 y 255 caracteres
        - description debe tener al menos 10 caracteres
        - detected_at debe ser <= reported_at (si se proporciona reported_at)
        - assigned_to debe ser un email válido

    Example:
        >>> incident = IncidentCreate(
        ...     title="Ransomware Attack on Production Server",
        ...     description="Detected ransomware encryption activity...",
        ...     incident_type=IncidentType.RANSOMWARE,
        ...     severity=IncidentSeverity.CRITICAL,
        ...     detected_at=datetime.now(timezone.utc),
        ...     assigned_to="security-team@example.com",
        ...     related_assets=["srv-prod-01", "db-primary-02"]
        ... )
    """

    detected_at: datetime = Field(
        ...,
        description="Timestamp de detección del incidente",
        examples=["2026-02-06T10:00:00Z"],
    )
    reported_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de reporte formal (por defecto = detected_at)",
        examples=["2026-02-06T10:05:00Z"],
    )
    assigned_to: Optional[str] = Field(
        default=None,
        description="Email del usuario asignado al incidente",
        examples=["security-team@example.com"],
    )
    related_assets: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de assets afectados",
        examples=[["srv-prod-01", "db-primary-02"]],
    )
    response_plan: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Plan de respuesta inicial estructurado",
        examples=[
            {
                "phases": [
                    {
                        "name": "containment",
                        "actions": ["isolate_system", "block_network"],
                    }
                ]
            }
        ],
    )
    evidence: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Evidencia inicial recolectada",
        examples=[
            {
                "logs": ["firewall.log", "system.log"],
                "screenshots": ["screen001.png"],
            }
        ],
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "IncidentCreate":
        """
        Valida que detected_at sea <= reported_at.

        Si reported_at no se proporciona, se establece igual a detected_at.
        """
        if self.reported_at is None:
            self.reported_at = self.detected_at
        elif self.detected_at > self.reported_at:
            raise ValueError(
                "detected_at must be earlier than or equal to reported_at. "
                f"Got detected_at={self.detected_at}, reported_at={self.reported_at}"
            )
        return self


# ============================================================================
# UPDATE SCHEMA
# ============================================================================


class IncidentUpdate(BaseModel):
    """
    Schema para actualizar un incidente existente.

    Todos los campos son opcionales para permitir actualizaciones parciales.

    Attributes:
        title: Nuevo título (opcional)
        description: Nueva descripción (opcional)
        incident_type: Nuevo tipo (opcional, raro cambiar)
        severity: Nueva severidad (opcional, puede escalarse)
        status: Nuevo estado del ciclo de vida (opcional)
        assigned_to: Nuevo asignado (opcional)
        contained_at: Timestamp de contención (opcional)
        resolved_at: Timestamp de resolución (opcional)
        response_plan: Plan de respuesta actualizado (opcional)
        actions_taken: Lista de acciones ejecutadas (opcional)
        evidence: Evidencia adicional (opcional)
        related_assets: Assets afectados actualizados (opcional)
        impact_assessment: Evaluación de impacto (opcional)
        root_cause: Análisis de causa raíz (opcional)
        lessons_learned: Lecciones aprendidas (opcional)

    Validations:
        - Si se proporcionan timestamps, deben seguir orden lógico
        - status debe ser un valor válido del enum

    Example:
        >>> update = IncidentUpdate(
        ...     status=IncidentStatus.CONTAINED,
        ...     contained_at=datetime.now(timezone.utc),
        ...     actions_taken=[
        ...         {
        ...             "timestamp": "2026-02-06T12:00:00Z",
        ...             "action": "isolated_system",
        ...             "status": "completed"
        ...         }
        ...     ]
        ... )
    """

    title: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Título actualizado del incidente",
    )
    description: Optional[str] = Field(
        default=None,
        min_length=10,
        description="Descripción actualizada del incidente",
    )
    incident_type: Optional[IncidentType] = Field(
        default=None,
        description="Tipo de incidente actualizado (raro cambiar)",
    )
    severity: Optional[IncidentSeverity] = Field(
        default=None,
        description="Severidad actualizada (puede escalarse)",
    )
    status: Optional[IncidentStatus] = Field(
        default=None,
        description="Estado actualizado del ciclo de vida",
        examples=["contained", "eradicated", "recovered", "closed"],
    )
    assigned_to: Optional[str] = Field(
        default=None,
        description="Email del usuario asignado actualizado",
    )
    contained_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de contención del incidente",
    )
    resolved_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de resolución completa",
    )
    response_plan: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Plan de respuesta actualizado",
    )
    actions_taken: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Lista de acciones ejecutadas",
        examples=[
            [
                {
                    "timestamp": "2026-02-06T12:00:00Z",
                    "action": "isolated_system",
                    "description": "Isolated compromised server from network",
                    "status": "completed",
                    "performed_by": "security-team@example.com",
                }
            ]
        ],
    )
    evidence: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Evidencia adicional recolectada",
    )
    related_assets: Optional[List[str]] = Field(
        default=None,
        description="Lista actualizada de assets afectados",
    )
    impact_assessment: Optional[str] = Field(
        default=None,
        description="Evaluación de impacto en el negocio",
        examples=[
            "Production web server compromised. Estimated 2 hours downtime. "
            "No customer data exposure confirmed."
        ],
    )
    root_cause: Optional[str] = Field(
        default=None,
        description="Análisis de causa raíz del incidente",
        examples=[
            "Unpatched vulnerability CVE-2025-1234 exploited via phishing email. "
            "User clicked malicious link leading to credential compromise."
        ],
    )
    lessons_learned: Optional[str] = Field(
        default=None,
        description="Lecciones aprendidas para prevención futura",
        examples=[
            "Need to improve patch management process. "
            "Deploy enhanced email filtering. "
            "Conduct security awareness training."
        ],
    )

    @model_validator(mode="after")
    def validate_timestamps(self) -> "IncidentUpdate":
        """
        Valida el orden lógico de timestamps si se proporcionan.

        contained_at y resolved_at deben seguir un orden cronológico lógico.
        """
        if self.contained_at and self.resolved_at:
            if self.contained_at > self.resolved_at:
                raise ValueError(
                    "contained_at must be earlier than or equal to resolved_at. "
                    f"Got contained_at={self.contained_at}, resolved_at={self.resolved_at}"
                )
        return self


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class IncidentResponse(IncidentBase):
    """
    Schema de respuesta completo para un incidente.

    Incluye todos los campos del modelo más campos computados.

    Attributes:
        id: UUID único del incidente
        incident_number: Número de incidente único (e.g., INC-2026-001)
        status: Estado actual del ciclo de vida
        detected_at: Timestamp de detección
        reported_at: Timestamp de reporte formal
        contained_at: Timestamp de contención (opcional)
        resolved_at: Timestamp de resolución (opcional)
        assigned_to: Email del asignado (opcional)
        response_plan: Plan de respuesta estructurado (opcional)
        actions_taken: Lista de acciones ejecutadas (opcional)
        evidence: Evidencia recolectada (opcional)
        related_assets: Lista de assets afectados (opcional)
        impact_assessment: Evaluación de impacto (opcional)
        root_cause: Causa raíz (opcional)
        lessons_learned: Lecciones aprendidas (opcional)
        resolution_time: Tiempo de resolución en horas (computado, opcional)
        created_at: Timestamp de creación del registro
        updated_at: Timestamp de última actualización

    Configuration:
        from_attributes=True: Permite crear desde modelos SQLAlchemy

    Example:
        >>> # Crear desde modelo SQLAlchemy
        >>> incident_model = Incident(...)
        >>> response = IncidentResponse.model_validate(incident_model)
    """

    model_config = ConfigDict(from_attributes=True, use_enum_values=False)

    id: UUID = Field(
        ...,
        description="UUID único del incidente",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    incident_number: str = Field(
        ...,
        description="Número de incidente único",
        examples=["INC-2026-001"],
    )
    status: IncidentStatus = Field(
        ...,
        description="Estado actual del ciclo de vida",
        examples=["contained"],
    )
    detected_at: datetime = Field(
        ...,
        description="Timestamp de detección",
    )
    reported_at: datetime = Field(
        ...,
        description="Timestamp de reporte formal",
    )
    contained_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de contención",
    )
    resolved_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de resolución completa",
    )
    assigned_to: Optional[str] = Field(
        default=None,
        description="Email del usuario asignado",
    )
    response_plan: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Plan de respuesta estructurado",
    )
    actions_taken: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Lista de acciones ejecutadas",
    )
    evidence: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Evidencia recolectada",
    )
    related_assets: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs de assets afectados",
    )
    impact_assessment: Optional[str] = Field(
        default=None,
        description="Evaluación de impacto",
    )
    root_cause: Optional[str] = Field(
        default=None,
        description="Análisis de causa raíz",
    )
    lessons_learned: Optional[str] = Field(
        default=None,
        description="Lecciones aprendidas",
    )
    resolution_time: Optional[float] = Field(
        default=None,
        description="Tiempo de resolución en horas (computado)",
        examples=[4.5],
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp de creación del registro",
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp de última actualización",
    )

    @model_validator(mode="after")
    def compute_resolution_time(self) -> "IncidentResponse":
        """
        Calcula resolution_time si detected_at y resolved_at están disponibles.

        Returns:
            Self con resolution_time calculado en horas
        """
        if self.detected_at and self.resolved_at:
            time_delta = self.resolved_at - self.detected_at
            self.resolution_time = time_delta.total_seconds() / 3600  # Horas
        return self


class IncidentSummary(BaseModel):
    """
    Schema resumido para listados de incidentes.

    Solo incluye campos esenciales para vistas de lista y búsqueda rápida.

    Attributes:
        id: UUID único del incidente
        incident_number: Número de incidente único
        title: Título descriptivo
        incident_type: Tipo de incidente
        severity: Nivel de severidad
        status: Estado actual
        detected_at: Timestamp de detección
        assigned_to: Email del asignado (opcional)
        resolution_time: Tiempo de resolución en horas (opcional)

    Example:
        >>> summaries = [
        ...     IncidentSummary(
        ...         id=uuid4(),
        ...         incident_number="INC-2026-001",
        ...         title="Ransomware Attack",
        ...         incident_type=IncidentType.RANSOMWARE,
        ...         severity=IncidentSeverity.CRITICAL,
        ...         status=IncidentStatus.RESOLVED,
        ...         detected_at=datetime.now(timezone.utc),
        ...         resolution_time=4.5
        ...     )
        ... ]
    """

    model_config = ConfigDict(from_attributes=True, use_enum_values=False)

    id: UUID = Field(
        ...,
        description="UUID único del incidente",
    )
    incident_number: str = Field(
        ...,
        description="Número de incidente único",
        examples=["INC-2026-001"],
    )
    title: str = Field(
        ...,
        description="Título descriptivo del incidente",
    )
    incident_type: IncidentType = Field(
        ...,
        description="Tipo de incidente",
    )
    severity: IncidentSeverity = Field(
        ...,
        description="Nivel de severidad",
    )
    status: IncidentStatus = Field(
        ...,
        description="Estado actual",
    )
    detected_at: datetime = Field(
        ...,
        description="Timestamp de detección",
    )
    assigned_to: Optional[str] = Field(
        default=None,
        description="Email del usuario asignado",
    )
    resolution_time: Optional[float] = Field(
        default=None,
        description="Tiempo de resolución en horas",
    )


class IncidentTimelineEvent(BaseModel):
    """
    Schema para eventos en la línea de tiempo de un incidente.

    Representa un evento individual en la cronología del incidente.

    Attributes:
        timestamp: Momento del evento
        event: Nombre/tipo del evento
        status: Estado asociado al evento
        description: Descripción del evento
        performed_by: Usuario que ejecutó la acción (opcional)
        metadata: Metadatos adicionales del evento (opcional)

    Example:
        >>> event = IncidentTimelineEvent(
        ...     timestamp=datetime.now(timezone.utc),
        ...     event="Incident Detected",
        ...     status="detected",
        ...     description="Initial detection of security incident",
        ...     performed_by="system",
        ...     metadata={"source": "SIEM", "alert_id": "ALT-12345"}
        ... )
    """

    timestamp: datetime = Field(
        ...,
        description="Timestamp del evento",
    )
    event: str = Field(
        ...,
        description="Nombre o tipo del evento",
        examples=[
            "Incident Detected",
            "Incident Assigned",
            "System Isolated",
            "Incident Contained",
            "Incident Resolved",
        ],
    )
    status: str = Field(
        ...,
        description="Estado asociado al evento",
        examples=["detected", "investigating", "contained", "resolved"],
    )
    description: str = Field(
        ...,
        description="Descripción detallada del evento",
        examples=[
            "Initial detection of security incident",
            "System isolated from network",
            "Malware removed from affected systems",
        ],
    )
    performed_by: Optional[str] = Field(
        default=None,
        description="Usuario o sistema que ejecutó la acción",
        examples=["security-team@example.com", "system", "incident-bot"],
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadatos adicionales del evento",
        examples=[{"source": "SIEM", "alert_id": "ALT-12345", "confidence": 0.95}],
    )


# ============================================================================
# PAGINATION SCHEMA
# ============================================================================


class IncidentListResponse(BaseModel):
    """
    Schema de respuesta paginada para listados de incidentes.

    Attributes:
        total: Total de incidentes que cumplen los filtros
        page: Número de página actual
        page_size: Tamaño de página
        items: Lista de incidentes resumidos
    """

    total: int = Field(
        ...,
        description="Total de incidentes que cumplen los filtros",
        examples=[150],
    )
    page: int = Field(
        ...,
        ge=1,
        description="Número de página actual",
        examples=[1],
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Tamaño de página",
        examples=[20],
    )
    items: List[IncidentSummary] = Field(
        ...,
        description="Lista de incidentes resumidos",
    )

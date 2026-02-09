"""
Shared Models - SQLAlchemy Base Models
======================================

Modelos base de SQLAlchemy que son heredados por todos los modelos
de la aplicación.

Contenido:
- Base          → Clase base declarativa de SQLAlchemy
- TimestampMixin → Mixin con created_at, updated_at
- UUIDMixin     → Mixin para IDs UUID
- SoftDeleteMixin → Mixin para soft delete
- Risk          → Modelo de riesgos de seguridad
- RiskSeverity  → Enum para severidad de riesgos
- RiskLikelihood → Enum para probabilidad de riesgos
- RiskStatus    → Enum para estado de riesgos
- RiskCategory  → Enum para categoría de riesgos
- ConversationSession → Modelo de sesiones de conversación
- ConversationMessage → Modelo de mensajes de conversación
- MessageRole   → Enum para roles de mensajes
- Incident      → Modelo de incidentes de seguridad
- IncidentType  → Enum para tipos de incidentes
- IncidentSeverity → Enum para severidad de incidentes
- IncidentStatus → Enum para estado del ciclo de vida de incidentes

Ejemplo de uso:
    from app.shared.models import Base, TimestampMixin, Risk, RiskSeverity
    from app.shared.models import Incident, IncidentType

    class MyModel(Base, TimestampMixin):
        __tablename__ = "my_models"
        id = Column(UUID, primary_key=True)
        title = Column(String, nullable=False)
"""

from app.shared.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.shared.models.enums import (
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    RiskCategory,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
)
from app.shared.models.risk import Risk
from app.shared.models.conversation import (
    ConversationSession,
    ConversationMessage,
    MessageRole,
)
from app.features.incident_response.models.incident import Incident


__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    "Risk",
    "RiskSeverity",
    "RiskLikelihood",
    "RiskStatus",
    "RiskCategory",
    "ConversationSession",
    "ConversationMessage",
    "MessageRole",
    "Incident",
    "IncidentType",
    "IncidentSeverity",
    "IncidentStatus",
]

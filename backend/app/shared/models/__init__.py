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

Ejemplo de uso:
    from app.shared.models import Base, TimestampMixin, Risk, RiskSeverity

    class MyModel(Base, TimestampMixin):
        __tablename__ = "my_models"
        id = Column(UUID, primary_key=True)
        title = Column(String, nullable=False)
"""

from app.shared.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.shared.models.enums import (
    RiskCategory,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
)
from app.shared.models.risk import Risk


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
]

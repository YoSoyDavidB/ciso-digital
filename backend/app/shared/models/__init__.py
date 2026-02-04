"""
Shared Models - SQLAlchemy Base Models
======================================

Modelos base de SQLAlchemy que son heredados por todos los modelos
de la aplicación.

Contenido esperado:
- Base          → Clase base declarativa de SQLAlchemy
- TimestampMixin → Mixin con created_at, updated_at
- UUIDMixin     → Mixin para IDs UUID
- SoftDeleteMixin → Mixin para soft delete

Ejemplo de uso:
    from app.shared.models import Base, TimestampMixin

    class Risk(Base, TimestampMixin):
        __tablename__ = "risks"
        id = Column(UUID, primary_key=True)
        title = Column(String, nullable=False)
"""

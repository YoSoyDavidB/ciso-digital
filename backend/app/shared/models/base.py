"""
SQLAlchemy Base Models and Mixins.

Este módulo contiene la clase base declarativa y mixins reutilizables
para todos los modelos de la aplicación.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Clase base declarativa para todos los modelos SQLAlchemy.

    Todos los modelos deben heredar de esta clase.
    """

    pass


class TimestampMixin:
    """
    Mixin que agrega timestamps automáticos a los modelos.

    Campos:
        created_at: Timestamp de creación (automático)
        updated_at: Timestamp de última actualización (automático)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """
    Mixin que agrega un ID UUID como primary key.

    Campos:
        id: UUID primary key (generado automáticamente)
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin que implementa soft delete.

    Campos:
        deleted_at: Timestamp de borrado lógico (NULL si no está borrado)
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

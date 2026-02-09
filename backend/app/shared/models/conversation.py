"""
Conversation Models for CISO Digital.

Este módulo define los modelos SQLAlchemy para la gestión de conversaciones
y memoria conversacional del sistema.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base import Base, TimestampMixin, UUIDMixin


class MessageRole(str, Enum):
    """
    Rol del mensaje en la conversación.
    
    Attributes:
        USER: Mensaje del usuario
        ASSISTANT: Respuesta del asistente IA
        SYSTEM: Mensaje del sistema (instrucciones, contexto)
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationSession(Base, UUIDMixin, TimestampMixin):
    """
    Sesión de conversación entre usuario y el sistema CISO Digital.
    
    Una sesión agrupa múltiples mensajes relacionados en un contexto
    conversacional. El título se genera automáticamente desde el
    primer mensaje del usuario.
    
    Attributes:
        id: UUID primary key
        user_id: UUID del usuario propietario de la sesión
        title: Título opcional (auto-generado del primer mensaje)
        extra_metadata: Metadatos JSON (contexto inicial, configuración)
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
        messages: Relación con mensajes de la sesión
    
    Example:
        >>> session = ConversationSession(
        ...     user_id=user.id,
        ...     title="Security Risk Assessment Discussion",
        ...     extra_metadata={"channel": "web", "ip": "192.168.1.1"}
        ... )
    """
    
    __tablename__ = "conversation_sessions"
    
    # Foreign Key a User (asumiendo que existe tabla users)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ForeignKey("users.id"),  # Descomentar cuando exista tabla users
        nullable=False,
        index=True,
    )
    
    # Título opcional (auto-generado del primer mensaje)
    title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # Extra metadata JSON flexible (nota: 'metadata' está reservado en SQLAlchemy)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata",  # Nombre de la columna en la BD
        JSON,
        nullable=True,
        default=dict,
    )
    
    # Relación con mensajes
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.timestamp",
    )
    
    def __repr__(self) -> str:
        return (
            f"<ConversationSession(id={self.id}, "
            f"user_id={self.user_id}, "
            f"title='{self.title[:30] if self.title else None}...', "
            f"messages={len(self.messages)})>"
        )


class ConversationMessage(Base, UUIDMixin):
    """
    Mensaje individual dentro de una sesión de conversación.
    
    Almacena el contenido del mensaje, el rol del emisor (user/assistant/system),
    y metadata adicional como el agente que lo generó, tokens consumidos,
    y otra información relevante.
    
    Attributes:
        id: UUID primary key
        session_id: UUID de la sesión a la que pertenece
        role: Rol del mensaje (user, assistant, system)
        content: Contenido textual del mensaje
        agent_used: Nombre del agente que generó la respuesta (opcional)
        tokens_consumed: Número de tokens consumidos (opcional)
        extra_metadata: Metadatos JSON (confidence, sources, etc.)
        timestamp: Fecha y hora del mensaje
        session: Relación con la sesión
    
    Example:
        >>> message = ConversationMessage(
        ...     session_id=session.id,
        ...     role=MessageRole.USER,
        ...     content="What are the critical security risks?",
        ...     extra_metadata={"intent": "risk_assessment"}
        ... )
    """
    
    __tablename__ = "conversation_messages"
    
    # Foreign Key a ConversationSession
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Rol del mensaje (user, assistant, system)
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole, name="message_role", native_enum=False),
        nullable=False,
        index=True,
    )
    
    # Contenido del mensaje
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # Agente que generó la respuesta (solo para role=assistant)
    agent_used: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    
    # Tokens consumidos en la generación (solo para role=assistant)
    tokens_consumed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    
    # Extra metadata JSON flexible (nota: 'metadata' está reservado en SQLAlchemy)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata",  # Nombre de la columna en la BD
        JSON,
        nullable=True,
        default=dict,
    )
    
    # Timestamp del mensaje
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    
    # Relación con sesión
    session: Mapped["ConversationSession"] = relationship(
        "ConversationSession",
        back_populates="messages",
    )
    
    def __repr__(self) -> str:
        return (
            f"<ConversationMessage(id={self.id}, "
            f"role={self.role.value}, "
            f"content='{self.content[:50]}...', "
            f"agent={self.agent_used})>"
        )

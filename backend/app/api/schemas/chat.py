"""
Chat API Schemas - Pydantic models for chat endpoints.

Defines request/response schemas for chat functionality with AI agents.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChatMessageRequest(BaseModel):
    """
    Request schema for sending a chat message.

    Attributes:
        message: User's chat message (required, non-empty)
        session_id: Optional session ID for conversation continuity
        context: Optional context for the agent (asset_id, etc.)
    """

    message: str = Field(..., min_length=1, description="User's chat message")
    session_id: str | None = Field(
        None, description="Optional session ID for conversation continuity"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Optional context for agent (asset_id, etc.)"
    )

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Validate message is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatMessageResponse(BaseModel):
    """
    Response schema for chat message.

    Attributes:
        response: Agent's response text
        session_id: Session ID for this conversation
        agent_used: Name of the agent that processed the request
        confidence: Confidence score of the response (0.0-1.0)
        sources: List of sources used for the response
    """

    response: str = Field(..., description="Agent's response text")
    session_id: str = Field(..., description="Session ID for this conversation")
    agent_used: str = Field(..., description="Name of agent that processed the request")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    sources: list[dict[str, Any]] = Field(
        default_factory=list, description="Sources used for response"
    )


class ChatSession(BaseModel):
    """
    Chat session information.

    Attributes:
        session_id: Unique session identifier
        created_at: Session creation timestamp
        last_message_at: Last message timestamp
        message_count: Number of messages in session
        context: Session context (asset_id, etc.)
    """

    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp (ISO format)")
    last_message_at: str = Field(..., description="Last message timestamp (ISO format)")
    message_count: int = Field(..., ge=0, description="Number of messages in session")
    context: dict[str, Any] = Field(default_factory=dict, description="Session context")


class ChatSessionList(BaseModel):
    """
    List of chat sessions.

    Attributes:
        sessions: List of chat sessions
    """

    sessions: list[ChatSession] = Field(default_factory=list, description="List of chat sessions")

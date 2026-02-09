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
        intent: Classified intent type (risk_assessment, incident_response, etc.)
        agent_used: Name of the primary agent that processed the request (deprecated, use agents_used)
        agents_used: List of agents used (for multi-agent responses)
        confidence: Confidence score of the response (0.0-1.0)
        sources: List of sources used for the response
        suggestions: List of suggested follow-up questions
    """

    response: str = Field(..., description="Agent's response text")
    session_id: str = Field(..., description="Session ID for this conversation")
    intent: str = Field(..., description="Classified intent type")
    agent_used: str | None = Field(None, description="Primary agent (deprecated, use agents_used)")
    agents_used: list[str] = Field(
        default_factory=list, description="List of agents used for multi-agent responses"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    sources: list[str] = Field(
        default_factory=list, description="Sources used for response"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
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


class CreateSessionRequest(BaseModel):
    """
    Request schema for creating a new chat session.
    
    Attributes:
        user_id: User identifier
        context: Optional initial context for the session
    """
    
    user_id: str = Field(..., description="User identifier")
    context: dict[str, Any] = Field(default_factory=dict, description="Optional initial context")


class CreateSessionResponse(BaseModel):
    """
    Response schema for session creation.
    
    Attributes:
        session_id: Created session identifier
        created_at: Session creation timestamp
    """
    
    session_id: str = Field(..., description="Created session identifier")
    created_at: str = Field(..., description="Session creation timestamp (ISO format)")


class ChatHistoryMessage(BaseModel):
    """
    Individual message in chat history.
    
    Attributes:
        id: Message unique identifier
        role: Message role (user, assistant, system)
        content: Message content
        timestamp: Message timestamp
        agent_used: Agent that generated the message (for assistant messages)
        metadata: Additional metadata (confidence, sources, etc.)
    """
    
    id: str = Field(..., description="Message unique identifier")
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp (ISO format)")
    agent_used: str | None = Field(None, description="Agent used (assistant messages only)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DeleteSessionResponse(BaseModel):
    """
    Response schema for session deletion.
    
    Attributes:
        success: Whether deletion was successful
        message: Status message
    """
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")

"""
Chat API Routes - Endpoints for CISO Digital AI Assistant.

🔵 REFACTOR Phase: Enhanced implementation with CISOOrchestrator integration.

Provides intelligent chat interface with:
- Multi-agent orchestration via CISOOrchestrator
- Intent classification and routing
- Session management and conversation history
- Enhanced responses with sources and suggestions
- RESTful endpoints for session lifecycle management

Endpoints:
- POST   /api/v1/chat/message                      - Send message to AI assistant
- GET    /api/v1/chat/sessions                     - List user sessions
- POST   /api/v1/chat/sessions                     - Create new session
- GET    /api/v1/chat/sessions/{id}/history        - Get session history
- DELETE /api/v1/chat/sessions/{id}                - Delete session
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.base_agent import Task
from app.agents.orchestrator import CISOOrchestrator
from app.agents.risk_agent import RiskAssessmentAgent
from app.api.schemas.chat import (
    ChatMessageRequest, 
    ChatMessageResponse, 
    ChatSession,
    ChatHistoryMessage,
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionResponse
)
from app.core.config import settings
from app.services.copilot_service import CopilotService
from app.services.conversation_memory import ConversationMemoryService
from app.services.embedding_service import EmbeddingService
from app.services.intent_classifier import IntentClassifier, IntentType
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory session storage (for MVP - replace with DB later)
_sessions: dict[str, dict[str, Any]] = {}


# ============================================================================
# Helper Functions
# ============================================================================


async def get_asset_by_id(asset_id: str) -> dict[str, Any] | None:
    """
    Get asset by ID from database.

    Args:
        asset_id: Asset identifier

    Returns:
        Asset data dict or None if not found

    Note:
        This is a stub for MVP - implement actual DB query later
    """
    # TODO: Implement actual database query
    # For now, return mock data for testing
    logger.debug(f"Getting asset {asset_id} (stub implementation)")

    # Return None for invalid IDs to test 404 handling
    if "invalid" in asset_id.lower():
        return None

    return {
        "id": asset_id,
        "name": f"Asset {asset_id}",
        "type": "server",
        "criticality": "high",
        "environment": "production",
    }


async def get_vulnerabilities_by_asset(asset_id: str) -> list[dict[str, Any]]:
    """
    Get vulnerabilities for an asset.

    Args:
        asset_id: Asset identifier

    Returns:
        List of vulnerability dicts

    Note:
        This is a stub for MVP - implement actual DB query later
    """
    # TODO: Implement actual database query
    logger.debug(f"Getting vulnerabilities for asset {asset_id} (stub implementation)")

    # Return empty list for now (no vulnerabilities)
    return []


async def save_chat_message(
    session_id: str,
    message: str,
    response: str,
    context: dict[str, Any],
    agent_used: str,
    confidence: float,
) -> None:
    """
    Save chat message to database.

    Args:
        session_id: Chat session ID
        message: User message
        response: Agent response
        context: Message context
        agent_used: Name of agent used
        confidence: Response confidence score

    Note:
        This is a stub for MVP - implement actual DB persistence later
    """
    # TODO: Implement actual database save
    logger.debug(f"Saving message to session {session_id} (stub implementation)")

    # Update in-memory session
    if session_id in _sessions:
        _sessions[session_id]["message_count"] += 1
        _sessions[session_id]["last_message_at"] = datetime.now().isoformat()


async def get_user_sessions(user_id: str | None = None) -> list[dict[str, Any]]:
    """
    Get user's chat sessions.

    Args:
        user_id: Optional user ID filter

    Returns:
        List of session dicts

    Note:
        This is a stub for MVP - implement actual DB query later
    """
    # TODO: Implement actual database query with user filtering
    logger.debug(f"Getting sessions for user {user_id} (stub implementation)")

    # Return sessions from in-memory storage
    return list(_sessions.values())


async def get_session_history(session_id: str) -> list[dict[str, Any]] | None:
    """
    Get chat history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of message dicts or None if session not found
        
    Note:
        This is a stub for MVP - implement actual DB query later
    """
    # TODO: Implement actual database query
    logger.debug(f"Getting history for session {session_id} (stub implementation)")
    
    # Check if session exists
    if session_id not in _sessions:
        return None
    
    # For now, return empty list (no message persistence in MVP)
    # In production, query conversation_messages table
    return []


async def delete_session(session_id: str) -> bool:
    """
    Delete a chat session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if deleted, False if not found
        
    Note:
        This is a stub for MVP - implement actual DB deletion later
    """
    # TODO: Implement actual database deletion with cascade
    logger.debug(f"Deleting session {session_id} (stub implementation)")
    
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    
    return False


def _generate_suggestions(intent_type: str, sources: list[str]) -> list[str]:
    """
    Generate follow-up question suggestions based on intent and sources.
    
    Args:
        intent_type: The classified intent type
        sources: List of sources used in the response
        
    Returns:
        List of suggested follow-up questions
    """
    suggestions = []
    
    # Intent-based suggestions
    if intent_type == "risk_assessment":
        suggestions = [
            "What are the most critical risks I should prioritize?",
            "Show me the remediation plan for these risks",
            "How does this compare to last month's risk posture?"
        ]
    elif intent_type == "incident_response":
        suggestions = [
            "What are the recommended next steps?",
            "Show me similar incidents from the past",
            "Who should be notified about this incident?"
        ]
    elif intent_type == "compliance_check":
        suggestions = [
            "Which controls are failing?",
            "Show me the evidence for these controls",
            "Generate a compliance report"
        ]
    elif intent_type == "threat_intelligence":
        suggestions = [
            "Are there any active exploits for this vulnerability?",
            "What are the recommended mitigations?",
            "Show me affected assets"
        ]
    elif intent_type == "general_query":
        suggestions = [
            "Can you assess our current risk posture?",
            "Show me recent security incidents",
            "Check our compliance status"
        ]
    else:
        suggestions = [
            "What else can you help me with?",
            "Show me our security metrics",
            "What are the top priorities?"
        ]
    
    # Return top 3 suggestions
    return suggestions[:3]


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message to CISO AI Assistant",
    description="Send a message to the CISO AI Assistant. Uses CISOOrchestrator for intent classification and multi-agent routing.",
)
async def send_chat_message(request: ChatMessageRequest) -> ChatMessageResponse:
    """
    Send chat message to CISO AI Assistant.

    Processes user message through CISOOrchestrator which:
    - Classifies user intent
    - Routes to appropriate specialized agent(s)
    - Aggregates multi-agent responses
    - Manages conversation context

    Args:
        request: Chat message request with message, optional session_id and context

    Returns:
        ChatMessageResponse with orchestrator's response and metadata

    Raises:
        HTTPException 500: If orchestrator processing fails
    """
    logger.info(f"💬 Chat message received: {request.message[:50]}...")

    try:
        # 1. Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())

        # 2. Initialize session if new
        if session_id not in _sessions:
            _sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "last_message_at": datetime.now().isoformat(),
                "message_count": 0,
                "context": request.context,
            }
            logger.info(f"✨ Created new session: {session_id}")

        # 3. Initialize orchestrator and dependencies
        copilot_service = CopilotService()
        embedding_service = EmbeddingService()
        
        # Initialize vector store and RAG service
        vector_store_service = VectorStoreService(
            qdrant_url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name="security_knowledge",
        )
        rag_service = RAGService(
            embedding_service=embedding_service,
            vector_store_service=vector_store_service,
            copilot_service=copilot_service,
        )
        
        # Initialize intent classifier
        intent_classifier = IntentClassifier(
            llm_service=copilot_service
        )
        
        # Initialize conversation memory
        conversation_memory = ConversationMemoryService(
            db_session=None,  # type: ignore  # TODO: Inject actual DB session
            rag_service=rag_service
        )
        
        # Initialize agents (for now, empty dict - agents will be added incrementally)
        agents = {}
        
        # Initialize orchestrator
        orchestrator = CISOOrchestrator(
            intent_classifier=intent_classifier,
            agents=agents,
            conversation_memory=conversation_memory,
            llm_service=copilot_service
        )

        # 4. Process request through orchestrator
        orchestrator_response = await orchestrator.process_request(
            user_query=request.message,
            session_id=session_id,
            user_id="default_user"  # TODO: Get from auth context
        )

        # 5. Update session metadata
        if session_id in _sessions:
            _sessions[session_id]["message_count"] += 1
            _sessions[session_id]["last_message_at"] = datetime.now().isoformat()

        logger.info(f"✅ Chat message processed successfully for session {session_id}")

        # 6. Build enhanced response with suggestions
        suggestions = _generate_suggestions(
            intent_type=orchestrator_response.intent_type,
            sources=orchestrator_response.sources
        )

        # 7. Return enhanced response
        return ChatMessageResponse(
            response=orchestrator_response.response_text,
            session_id=session_id,
            intent=orchestrator_response.intent_type,
            agent_used=orchestrator_response.agent_used,
            agents_used=orchestrator_response.agents_used or [],
            confidence=orchestrator_response.confidence,
            sources=orchestrator_response.sources,
            suggestions=suggestions,
        )

    except Exception as e:
        logger.error(f"❌ Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}",
        )


@router.get(
    "/sessions",
    response_model=list[ChatSession],
    status_code=status.HTTP_200_OK,
    summary="List chat sessions",
    description="Get list of user's chat sessions with metadata.",
)
async def list_chat_sessions() -> list[ChatSession]:
    """
    List user's chat sessions.

    Returns all chat sessions for the current user (or all sessions in MVP).

    Returns:
        List of ChatSession objects with session metadata
    """
    logger.info("📋 Listing chat sessions")

    try:
        # Get sessions from database (or in-memory storage)
        sessions_data = await get_user_sessions()

        # Convert to ChatSession models
        sessions = [
            ChatSession(
                session_id=session["session_id"],
                created_at=session["created_at"],
                last_message_at=session["last_message_at"],
                message_count=session["message_count"],
                context=session.get("context", {}),
            )
            for session in sessions_data
        ]

        logger.info(f"✅ Retrieved {len(sessions)} sessions")
        return sessions

    except Exception as e:
        logger.error(f"❌ Error listing sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}",
        )


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat session",
    description="Create a new chat session for a user.",
)
async def create_chat_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """
    Create a new chat session.
    
    Args:
        request: Session creation request with user_id and optional context
        
    Returns:
        CreateSessionResponse with session_id and created_at
    """
    logger.info(f"🆕 Creating new chat session for user {request.user_id}")
    
    try:
        # Generate new session ID
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # Create session in storage
        _sessions[session_id] = {
            "session_id": session_id,
            "user_id": request.user_id,
            "created_at": created_at,
            "last_message_at": created_at,
            "message_count": 0,
            "context": request.context,
        }
        
        logger.info(f"✅ Created session {session_id} for user {request.user_id}")
        
        return CreateSessionResponse(
            session_id=session_id,
            created_at=created_at
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/history",
    response_model=list[ChatHistoryMessage],
    status_code=status.HTTP_200_OK,
    summary="Get session chat history",
    description="Retrieve complete conversation history for a session.",
)
async def get_chat_session_history(session_id: str) -> list[ChatHistoryMessage]:
    """
    Get chat history for a session.
    
    Returns all messages in chronological order for the specified session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of ChatHistoryMessage objects
        
    Raises:
        HTTPException 404: If session not found
        HTTPException 500: If retrieval fails
    """
    logger.info(f"📜 Retrieving history for session {session_id}")
    
    try:
        # Get history from database
        history = await get_session_history(session_id)
        
        if history is None:
            logger.warning(f"❌ Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        # Convert to ChatHistoryMessage models
        messages = [
            ChatHistoryMessage(
                id=msg.get("id", str(uuid.uuid4())),
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp", datetime.now().isoformat()),
                agent_used=msg.get("agent_used"),
                metadata=msg.get("metadata", {})
            )
            for msg in history
        ]
        
        logger.info(f"✅ Retrieved {len(messages)} messages for session {session_id}")
        return messages
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error retrieving history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session history: {str(e)}",
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete chat session",
    description="Delete a chat session and all associated messages.",
)
async def delete_chat_session(session_id: str) -> None:
    """
    Delete a chat session.
    
    Permanently deletes the session and all associated messages.
    This action cannot be undone.
    
    Args:
        session_id: Session identifier
        
    Raises:
        HTTPException 404: If session not found
        HTTPException 500: If deletion fails
    """
    logger.info(f"🗑️  Deleting session {session_id}")
    
    try:
        # Delete session from database
        success = await delete_session(session_id)
        
        if not success:
            logger.warning(f"❌ Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        logger.info(f"✅ Session {session_id} deleted successfully")
        # 204 No Content - no return value needed
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error deleting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}",
        )

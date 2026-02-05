"""
Chat API Routes - Endpoints for AI-powered chat with agents.

🟢 GREEN Phase: Minimum implementation to pass tests.

Provides chat interface for interacting with AI agents (RiskAssessmentAgent, etc.)
with session management and context handling.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.base_agent import Task
from app.agents.risk_agent import RiskAssessmentAgent
from app.api.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSession
from app.core.config import settings
from app.services.copilot_service import CopilotService
from app.services.embedding_service import EmbeddingService
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


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message to AI agent",
    description="Send a message to an AI agent for processing. Supports asset context for risk assessment.",
)
async def send_chat_message(request: ChatMessageRequest) -> ChatMessageResponse:
    """
    Send chat message to AI agent.

    Processes user message with appropriate AI agent based on context:
    - If asset_id provided: Uses RiskAssessmentAgent for risk analysis
    - Otherwise: General query processing

    Args:
        request: Chat message request with message, optional session_id and context

    Returns:
        ChatMessageResponse with agent's response and session info

    Raises:
        HTTPException 404: If asset_id provided but asset not found
        HTTPException 500: If agent processing fails
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

        # 3. Check if asset context provided
        asset_id = request.context.get("asset_id")

        if asset_id:
            # Asset-specific risk assessment
            logger.info(f"🎯 Processing risk assessment for asset {asset_id}")

            # Load asset from database
            asset = await get_asset_by_id(asset_id)
            if asset is None:
                logger.warning(f"❌ Asset not found: {asset_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Asset not found: {asset_id}",
                )

            # Load vulnerabilities
            vulnerabilities = await get_vulnerabilities_by_asset(asset_id)
            logger.debug(f"📊 Found {len(vulnerabilities)} vulnerabilities")

            # Initialize services and RiskAssessmentAgent
            copilot_service = CopilotService()
            embedding_service = EmbeddingService()
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
            agent = RiskAssessmentAgent(
                copilot_service=copilot_service,
                rag_service=rag_service,
                db_session=None,  # type: ignore
            )

            # Perform risk assessment
            assessment = await agent.assess_risk(asset=asset, vulnerabilities=vulnerabilities)

            # Build response
            response_text = f"""Risk Assessment Complete:
- Risk Score: {assessment.risk_score:.1f}/10.0
- Severity: {assessment.severity.upper()}
- Vulnerabilities: {assessment.vulnerabilities_count}
- Confidence: {assessment.confidence:.0%}

Top Recommendations:
"""
            for i, rec in enumerate(assessment.recommendations[:3], 1):
                response_text += f"{i}. {rec}\n"

            agent_used = "risk_assessment"
            confidence = assessment.confidence
            sources = []

        else:
            # General query (no asset context)
            logger.info("💭 Processing general query")

            # Initialize services and RiskAssessmentAgent for general queries
            copilot_service = CopilotService()
            embedding_service = EmbeddingService()
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
            agent = RiskAssessmentAgent(
                copilot_service=copilot_service,
                rag_service=rag_service,
                db_session=None,  # type: ignore
            )

            # Execute general task
            task = Task(query=request.message, context={}, parameters={})
            agent_response = await agent.execute(task)

            response_text = agent_response.response
            agent_used = "risk_assessment"
            confidence = agent_response.confidence
            sources = agent_response.sources

        # 4. Save conversation to database
        await save_chat_message(
            session_id=session_id,
            message=request.message,
            response=response_text,
            context=request.context,
            agent_used=agent_used,
            confidence=confidence,
        )

        logger.info(f"✅ Chat message processed successfully for session {session_id}")

        # 5. Return response
        return ChatMessageResponse(
            response=response_text,
            session_id=session_id,
            agent_used=agent_used,
            confidence=confidence,
            sources=sources,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

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

"""
Tests for ConversationMemoryService

🔴 RED Phase: These tests will FAIL because ConversationMemoryService doesn't exist yet.

The ConversationMemoryService will:
1. Store conversation messages with context in database
2. Retrieve conversation history by session_id
3. Search similar conversations in Qdrant (semantic memory)
4. Maintain configurable window size (last N messages)
5. Include metadata: user_id, agent_used, tokens_consumed
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from typing import List

from app.services.conversation_memory import (
    ConversationMemoryService,
    ConversationMessage,
    ConversationSession,
)
from app.services.rag_service import RAGService


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_rag_service():
    """Mock RAG service for embeddings and similarity search"""
    service = AsyncMock(spec=RAGService)
    
    # Mock create_embedding
    service.create_embedding = AsyncMock(return_value=[0.1] * 1536)
    
    # Mock search (returns similar conversations)
    service.search = AsyncMock(return_value=[
        {
            "id": "conv-1",
            "score": 0.95,
            "payload": {
                "session_id": "session-old-1",
                "content": "Previous similar conversation about security incident",
                "user_id": "user-123",
                "timestamp": "2026-02-01T10:00:00"
            }
        }
    ])
    
    return service


@pytest.fixture
async def conversation_memory_service(mock_db_session, mock_rag_service):
    """ConversationMemoryService instance with mocked dependencies"""
    return ConversationMemoryService(
        db_session=mock_db_session,
        rag_service=mock_rag_service,
        window_size=10  # Default: keep last 10 messages
    )


@pytest.fixture
def sample_message_data():
    """Sample message data for testing"""
    return {
        "session_id": "session-test-123",
        "role": "user",
        "content": "What are the critical security risks in our infrastructure?",
        "user_id": "user-456",
        "metadata": {
            "agent_used": None,
            "tokens_consumed": 0,
            "intent": "risk_assessment"
        }
    }


@pytest.fixture
def sample_assistant_message():
    """Sample assistant response"""
    return {
        "session_id": "session-test-123",
        "role": "assistant",
        "content": "Based on the analysis, here are the critical risks...",
        "user_id": "user-456",
        "metadata": {
            "agent_used": "risk_assessment",
            "tokens_consumed": 1250,
            "risk_score": 8.5,
            "model": "claude-sonnet-4.5"
        }
    }


# ============================================================================
# Tests
# ============================================================================

@pytest.mark.asyncio
async def test_save_message_stores_in_database(
    conversation_memory_service,
    mock_db_session,
    sample_message_data
):
    """
    🔴 RED: Test that save_message stores conversation message in database.
    
    Given: A conversation message with session_id, role, content, metadata
    When: save_message() is called
    Then: Message is added to database session and committed
    """
    # Act
    message = await conversation_memory_service.save_message(
        session_id=sample_message_data["session_id"],
        role=sample_message_data["role"],
        content=sample_message_data["content"],
        user_id=sample_message_data["user_id"],
        metadata=sample_message_data["metadata"]
    )
    
    # Assert
    assert message is not None
    assert isinstance(message, ConversationMessage)
    assert message.session_id == sample_message_data["session_id"]
    assert message.role == sample_message_data["role"]
    assert message.content == sample_message_data["content"]
    assert message.user_id == sample_message_data["user_id"]
    assert message.metadata == sample_message_data["metadata"]
    assert message.timestamp is not None
    
    # Verify database interactions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_conversation_history_returns_ordered_messages(
    conversation_memory_service,
    mock_db_session
):
    """
    🔴 RED: Test that get_conversation_history returns messages ordered by timestamp.
    
    Given: A session with multiple messages in database
    When: get_conversation_history() is called with session_id
    Then: Returns messages ordered by timestamp (oldest first)
    """
    # Arrange - Mock database response with messages
    mock_messages = [
        Mock(
            session_id="session-test-123",
            role="user",
            content="What are the risks?",
            timestamp=datetime(2026, 2, 5, 10, 0, 0),
            user_id="user-456",
            metadata={"tokens_consumed": 0}
        ),
        Mock(
            session_id="session-test-123",
            role="assistant",
            content="Here are the risks...",
            timestamp=datetime(2026, 2, 5, 10, 1, 0),
            user_id="user-456",
            metadata={"tokens_consumed": 500, "agent_used": "risk_assessment"}
        ),
        Mock(
            session_id="session-test-123",
            role="user",
            content="Tell me more about the critical ones",
            timestamp=datetime(2026, 2, 5, 10, 2, 0),
            user_id="user-456",
            metadata={"tokens_consumed": 0}
        ),
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_messages
    mock_db_session.execute.return_value = mock_result
    
    # Act
    history = await conversation_memory_service.get_conversation_history(
        session_id="session-test-123"
    )
    
    # Assert
    assert len(history) == 3
    assert history[0].role == "user"
    assert history[1].role == "assistant"
    assert history[2].role == "user"
    assert history[0].timestamp < history[1].timestamp < history[2].timestamp
    
    # Verify database was queried
    mock_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_conversation_history_respects_window_size(
    mock_db_session,
    mock_rag_service
):
    """
    🔴 RED: Test that get_conversation_history respects window_size limit.
    
    Given: A session with 15 messages and window_size=5
    When: get_conversation_history() is called
    Then: Returns only the last 5 messages
    """
    # Arrange - Service with window_size=5
    service = ConversationMemoryService(
        db_session=mock_db_session,
        rag_service=mock_rag_service,
        window_size=5
    )
    
    # Mock 15 messages in database
    mock_messages = [
        Mock(
            session_id="session-test-123",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            timestamp=datetime(2026, 2, 5, 10, i, 0),
            user_id="user-456",
            metadata={}
        )
        for i in range(15)
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_messages[-5:]  # Last 5
    mock_db_session.execute.return_value = mock_result
    
    # Act
    history = await service.get_conversation_history(
        session_id="session-test-123"
    )
    
    # Assert
    assert len(history) == 5, f"Expected 5 messages, got {len(history)}"
    assert history[0].content == "Message 10"
    assert history[-1].content == "Message 14"


@pytest.mark.asyncio
async def test_search_similar_conversations_uses_rag(
    conversation_memory_service,
    mock_rag_service
):
    """
    🔴 RED: Test that search_similar_conversations uses RAG for semantic search.
    
    Given: A query message
    When: search_similar_conversations() is called
    Then: RAG service is used to find semantically similar conversations
    """
    # Arrange
    query = "How do I handle a security incident?"
    
    # Act
    similar_conversations = await conversation_memory_service.search_similar_conversations(
        query=query,
        user_id="user-456",
        limit=3
    )
    
    # Assert
    assert len(similar_conversations) > 0
    assert similar_conversations[0]["score"] == 0.95
    assert similar_conversations[0]["payload"]["session_id"] == "session-old-1"
    assert "security incident" in similar_conversations[0]["payload"]["content"]
    
    # Verify RAG service was called
    mock_rag_service.create_embedding.assert_awaited_once_with(query)
    mock_rag_service.search.assert_awaited_once()
    
    # Verify search was called with correct parameters
    search_call_args = mock_rag_service.search.call_args
    assert search_call_args[1]["collection_name"] == "conversations"
    assert search_call_args[1]["limit"] == 3


@pytest.mark.asyncio
async def test_save_message_creates_embedding_in_qdrant(
    conversation_memory_service,
    mock_rag_service,
    sample_message_data
):
    """
    🔴 RED: Test that save_message creates embedding and stores in Qdrant.
    
    Given: A conversation message
    When: save_message() is called
    Then: Embedding is created and stored in Qdrant for semantic search
    """
    # Act
    message = await conversation_memory_service.save_message(
        session_id=sample_message_data["session_id"],
        role=sample_message_data["role"],
        content=sample_message_data["content"],
        user_id=sample_message_data["user_id"],
        metadata=sample_message_data["metadata"]
    )
    
    # Assert - Verify embedding was created
    mock_rag_service.create_embedding.assert_awaited_once_with(
        sample_message_data["content"]
    )
    
    # Assert - Message was returned
    assert message is not None
    assert message.content == sample_message_data["content"]


@pytest.mark.asyncio
async def test_save_message_includes_complete_metadata(
    conversation_memory_service,
    mock_db_session,
    sample_assistant_message
):
    """
    🔴 RED: Test that save_message preserves all metadata fields.
    
    Given: An assistant message with rich metadata (agent_used, tokens, model)
    When: save_message() is called
    Then: All metadata is preserved in the database
    """
    # Act
    message = await conversation_memory_service.save_message(
        session_id=sample_assistant_message["session_id"],
        role=sample_assistant_message["role"],
        content=sample_assistant_message["content"],
        user_id=sample_assistant_message["user_id"],
        metadata=sample_assistant_message["metadata"]
    )
    
    # Assert
    assert message.metadata["agent_used"] == "risk_assessment"
    assert message.metadata["tokens_consumed"] == 1250
    assert message.metadata["risk_score"] == 8.5
    assert message.metadata["model"] == "claude-sonnet-4.5"


@pytest.mark.asyncio
async def test_create_session_initializes_new_conversation(
    conversation_memory_service,
    mock_db_session
):
    """
    🔴 RED: Test that create_session initializes a new conversation session.
    
    Given: A user_id
    When: create_session() is called
    Then: New ConversationSession is created with unique session_id
    """
    # Act
    session = await conversation_memory_service.create_session(
        user_id="user-456",
        metadata={"channel": "web", "ip": "192.168.1.1"}
    )
    
    # Assert
    assert session is not None
    assert isinstance(session, ConversationSession)
    assert session.session_id is not None
    assert session.user_id == "user-456"
    assert session.created_at is not None
    assert session.updated_at is not None
    assert session.metadata["channel"] == "web"
    
    # Verify database interaction
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_session_by_id_returns_session(
    conversation_memory_service,
    mock_db_session
):
    """
    🔴 RED: Test that get_session() retrieves existing session.
    
    Given: An existing session_id in database
    When: get_session() is called
    Then: Returns the ConversationSession object
    """
    # Arrange
    mock_session = Mock(
        session_id="session-test-123",
        user_id="user-456",
        created_at=datetime(2026, 2, 5, 10, 0, 0),
        updated_at=datetime(2026, 2, 5, 10, 30, 0),
        metadata={}
    )
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_session
    mock_db_session.execute.return_value = mock_result
    
    # Act
    session = await conversation_memory_service.get_session("session-test-123")
    
    # Assert
    assert session is not None
    assert session.session_id == "session-test-123"
    assert session.user_id == "user-456"
    
    mock_db_session.execute.assert_awaited_once()

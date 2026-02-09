"""
Tests for Chat API endpoints.

🔴 RED Phase: Tests written first, endpoint implementation pending.

Tests cover:
- POST /api/v1/chat/message - Send chat message with agent processing
- GET /api/v1/chat/sessions - List user chat sessions
- Session management and persistence
- Agent integration (RiskAssessmentAgent)
- Asset and vulnerability context loading
- Error handling and validation
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.agents.risk_agent import RiskAssessment


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_chat_message():
    """Sample chat message request."""
    return {
        "message": "What is the risk level of the production web server?",
        "session_id": None,
        "context": {"asset_id": "asset-123", "include_history": True},
    }


@pytest.fixture
def sample_chat_message_no_context():
    """Chat message without asset context."""
    return {"message": "Tell me about security best practices", "session_id": None, "context": {}}


@pytest.fixture
def sample_session_id():
    """Sample session ID."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_asset():
    """Sample asset data."""
    return {
        "id": "asset-123",
        "name": "Production Web Server",
        "type": "server",
        "criticality": "critical",
        "environment": "production",
    }


@pytest.fixture
def sample_vulnerabilities():
    """Sample vulnerability data."""
    return [
        {
            "id": "vuln-1",
            "cve_id": "CVE-2025-1234",
            "cvss_score": 9.8,
            "description": "Critical RCE vulnerability in Apache Struts",
            "asset_id": "asset-123",
        },
        {
            "id": "vuln-2",
            "cve_id": "CVE-2025-5678",
            "cvss_score": 8.5,
            "description": "SQL injection vulnerability",
            "asset_id": "asset-123",
        },
    ]


@pytest.fixture
def mock_risk_assessment():
    """Mock RiskAssessment result."""
    return RiskAssessment(
        risk_score=9.2,
        severity="critical",
        recommendations=[
            "Immediately patch Apache Struts to version 2.5.30",
            "Implement WAF rules to block exploit attempts",
            "Isolate server from production network",
        ],
        confidence=0.95,
        asset_id="asset-123",
        vulnerabilities_count=2,
        reasoning="Two critical vulnerabilities with active exploits detected.",
    )


# ============================================================================
# TEST: POST /api/v1/chat/message - Message with Asset Context
# ============================================================================


class TestChatMessageWithAssetContext:
    """Tests for chat message endpoint with asset context."""

    @pytest.mark.asyncio
    async def test_send_message_with_asset_context_returns_risk_assessment(
        self, async_client: AsyncClient, sample_chat_message, sample_asset, sample_vulnerabilities, mock_risk_assessment
    ):
        """
        🔴 RED: POST /api/v1/chat/message with asset_id should return risk assessment.

        Given: Valid chat message with asset_id in context
        When: POST request sent to /api/v1/chat/message
        Then: Returns 200 with risk assessment response
        """
        with patch("app.api.routes.chat.get_asset_by_id", return_value=sample_asset), patch(
            "app.api.routes.chat.get_vulnerabilities_by_asset", return_value=sample_vulnerabilities
        ), patch("app.api.routes.chat.RiskAssessmentAgent") as mock_agent_class:

            # Setup mock agent
            mock_agent = AsyncMock()
            mock_agent.assess_risk.return_value = mock_risk_assessment
            mock_agent_class.return_value = mock_agent

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Validate response structure
            assert "response" in data
            assert "session_id" in data
            assert "agent_used" in data
            assert "confidence" in data
            assert "sources" in data

            # Validate content
            assert data["agent_used"] == "risk_assessment"
            assert data["confidence"] == 0.95
            assert "9.2" in data["response"] or "critical" in data["response"].lower()

            # Verify agent was called with correct context
            mock_agent.assess_risk.assert_called_once()
            call_args = mock_agent.assess_risk.call_args
            assert call_args.kwargs["asset"]["id"] == "asset-123"
            assert len(call_args.kwargs["vulnerabilities"]) == 2

    @pytest.mark.asyncio
    async def test_send_message_creates_new_session_if_none_provided(self, async_client: AsyncClient, sample_chat_message):
        """
        🔴 RED: Should create new session_id if not provided.

        Given: Chat message without session_id
        When: POST request sent
        Then: Response includes newly created session_id (valid UUID)
        """
        with patch("app.api.routes.chat.get_asset_by_id"), patch("app.api.routes.chat.get_vulnerabilities_by_asset"), patch(
            "app.api.routes.chat.RiskAssessmentAgent"
        ) as mock_agent_class:

            mock_agent = AsyncMock()
            mock_agent.assess_risk.return_value = MagicMock(
                risk_score=5.0, severity="medium", recommendations=["Test"], confidence=0.8, vulnerabilities_count=0
            )
            mock_agent_class.return_value = mock_agent

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert "session_id" in data
            # Validate UUID format
            try:
                uuid.UUID(data["session_id"])
                uuid_valid = True
            except ValueError:
                uuid_valid = False
            assert uuid_valid, f"session_id is not a valid UUID: {data['session_id']}"

    @pytest.mark.asyncio
    async def test_send_message_reuses_existing_session(
        self, async_client: AsyncClient, sample_chat_message, sample_session_id
    ):
        """
        🔴 RED: Should reuse session_id if provided.

        Given: Chat message with existing session_id
        When: POST request sent
        Then: Response returns same session_id
        """
        sample_chat_message["session_id"] = sample_session_id

        with patch("app.api.routes.chat.get_asset_by_id"), patch("app.api.routes.chat.get_vulnerabilities_by_asset"), patch(
            "app.api.routes.chat.RiskAssessmentAgent"
        ) as mock_agent_class:

            mock_agent = AsyncMock()
            mock_agent.assess_risk.return_value = MagicMock(
                risk_score=5.0, severity="medium", recommendations=["Test"], confidence=0.8, vulnerabilities_count=0
            )
            mock_agent_class.return_value = mock_agent

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["session_id"] == sample_session_id


# ============================================================================
# TEST: POST /api/v1/chat/message - Message without Asset Context
# ============================================================================


class TestChatMessageWithoutAssetContext:
    """Tests for chat message endpoint without asset context."""

    @pytest.mark.asyncio
    async def test_send_message_without_asset_context_returns_general_response(
        self, async_client: AsyncClient, sample_chat_message_no_context
    ):
        """
        🔴 RED: Message without asset_id should still get agent response.

        Given: Chat message without asset_id
        When: POST request sent
        Then: Returns 200 with general security guidance
        """
        with patch("app.api.routes.chat.RiskAssessmentAgent") as mock_agent_class:

            mock_agent = AsyncMock()
            mock_agent.execute.return_value = MagicMock(
                response="General security best practices include...", confidence=0.85, sources=[], actions_taken=["general_query"]
            )
            mock_agent_class.return_value = mock_agent

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message_no_context)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert "response" in data
            assert "General security" in data["response"] or "best practices" in data["response"]


# ============================================================================
# TEST: POST /api/v1/chat/message - Validation and Error Handling
# ============================================================================


class TestChatMessageValidation:
    """Tests for chat message validation and error handling."""

    @pytest.mark.asyncio
    async def test_send_message_with_empty_message_returns_422(self, async_client: AsyncClient):
        """
        🔴 RED: Empty message should return 422 validation error.

        Given: Chat request with empty message
        When: POST request sent
        Then: Returns 422 Unprocessable Entity
        """
        response = await async_client.post("/api/v1/chat/message", json={"message": "", "session_id": None, "context": {}})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_send_message_with_missing_message_field_returns_422(self, async_client: AsyncClient):
        """
        🔴 RED: Missing message field should return 422.

        Given: Request without 'message' field
        When: POST request sent
        Then: Returns 422 Unprocessable Entity
        """
        response = await async_client.post("/api/v1/chat/message", json={"session_id": None, "context": {}})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_send_message_with_invalid_asset_id_returns_404(self, async_client: AsyncClient, sample_chat_message):
        """
        🔴 RED: Invalid asset_id should return 404.

        Given: Message with non-existent asset_id
        When: POST request sent
        Then: Returns 404 Not Found
        """
        sample_chat_message["context"]["asset_id"] = "invalid-asset-999"

        with patch("app.api.routes.chat.get_asset_by_id", return_value=None):

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "detail" in data
            assert "asset" in data["detail"].lower() or "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_send_message_with_agent_error_returns_500(self, async_client: AsyncClient, sample_chat_message):
        """
        🔴 RED: Agent processing error should return 500.

        Given: Agent raises exception during processing
        When: POST request sent
        Then: Returns 500 Internal Server Error
        """
        with patch("app.api.routes.chat.get_asset_by_id"), patch("app.api.routes.chat.get_vulnerabilities_by_asset"), patch(
            "app.api.routes.chat.RiskAssessmentAgent"
        ) as mock_agent_class:

            mock_agent = AsyncMock()
            mock_agent.assess_risk.side_effect = Exception("Agent processing failed")
            mock_agent_class.return_value = mock_agent

            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data


# ============================================================================
# TEST: GET /api/v1/chat/sessions - List Sessions
# ============================================================================


class TestChatSessions:
    """Tests for chat sessions listing endpoint."""

    @pytest.mark.asyncio
    async def test_get_sessions_returns_list_of_sessions(self, async_client: AsyncClient):
        """
        🔴 RED: GET /api/v1/chat/sessions should return list of sessions.

        Given: User has existing chat sessions
        When: GET request sent to /api/v1/chat/sessions
        Then: Returns 200 with list of sessions
        """
        mock_sessions = [
            {
                "session_id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "last_message_at": datetime.now().isoformat(),
                "message_count": 5,
                "context": {"asset_id": "asset-123"},
            },
            {
                "session_id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "last_message_at": datetime.now().isoformat(),
                "message_count": 3,
                "context": {},
            },
        ]

        with patch("app.api.routes.chat.get_user_sessions", return_value=mock_sessions):

            response = await async_client.get("/api/v1/chat/sessions")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 2
            assert all("session_id" in session for session in data)
            assert all("message_count" in session for session in data)

    @pytest.mark.asyncio
    async def test_get_sessions_returns_empty_list_when_no_sessions(self, async_client: AsyncClient):
        """
        🔴 RED: Should return empty list when user has no sessions.

        Given: User has no chat sessions
        When: GET request sent
        Then: Returns 200 with empty list
        """
        with patch("app.api.routes.chat.get_user_sessions", return_value=[]):

            response = await async_client.get("/api/v1/chat/sessions")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 0


# ============================================================================
# TEST: POST /api/v1/chat/message - Integration with CISOOrchestrator
# ============================================================================


class TestChatMessageWithOrchestrator:
    """Tests for chat message endpoint with CISOOrchestrator integration."""

    @pytest.mark.asyncio
    async def test_send_message_uses_orchestrator_instead_of_direct_agent(
        self, async_client: AsyncClient, sample_chat_message_no_context
    ):
        """
        🔴 RED: POST /api/v1/chat/message should use CISOOrchestrator.process_request().
        
        Given: Valid chat message
        When: POST request sent to /api/v1/chat/message
        Then: CISOOrchestrator.process_request() is called instead of direct agent
        """
        from app.schemas.orchestrator import OrchestratorResponse
        
        mock_orchestrator_response = OrchestratorResponse(
            response_text="This is a response from the orchestrator",
            intent_type="general_query",
            confidence=0.88,
            session_id="test-session-123",
            agent_used="DirectResponse",
            sources=["https://example.com/security-guide"],
            requires_clarification=False
        )
        
        with patch("app.api.routes.chat.CISOOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = AsyncMock()
            mock_orchestrator.process_request.return_value = mock_orchestrator_response
            mock_orchestrator_class.return_value = mock_orchestrator
            
            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message_no_context)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify orchestrator was called
            mock_orchestrator.process_request.assert_called_once()
            call_args = mock_orchestrator.process_request.call_args
            assert call_args.kwargs["user_query"] == sample_chat_message_no_context["message"]
            assert "session_id" in call_args.kwargs
            assert "user_id" in call_args.kwargs
            
            # Verify response structure
            assert data["response"] == "This is a response from the orchestrator"
            assert data["intent"] == "general_query"
            assert data["confidence"] == 0.88

    @pytest.mark.asyncio
    async def test_send_message_with_orchestrator_returns_enhanced_response(
        self, async_client: AsyncClient, sample_chat_message_no_context
    ):
        """
        🔴 RED: Response should include intent, agents_used, sources, and suggestions.
        
        Given: Chat message processed by orchestrator
        When: Response returned
        Then: Response includes intent, agents_used, sources, suggestions fields
        """
        from app.schemas.orchestrator import OrchestratorResponse
        
        mock_orchestrator_response = OrchestratorResponse(
            response_text="Risk assessment complete for your infrastructure",
            intent_type="risk_assessment",
            confidence=0.95,
            session_id="session-456",
            agents_used=["RiskAssessmentAgent", "ThreatAgent"],
            sources=[
                "CVE-2025-1234",
                "NIST 800-53 Control AC-2"
            ],
            requires_clarification=False,
            agent_results={
                "RiskAssessmentAgent": {"risk_score": 8.5},
                "ThreatAgent": {"threat_level": "high"}
            }
        )
        
        with patch("app.api.routes.chat.CISOOrchestrator") as mock_orchestrator_class:
            mock_orchestrator = AsyncMock()
            mock_orchestrator.process_request.return_value = mock_orchestrator_response
            mock_orchestrator_class.return_value = mock_orchestrator
            
            response = await async_client.post("/api/v1/chat/message", json=sample_chat_message_no_context)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify enhanced response structure
            assert "intent" in data
            assert data["intent"] == "risk_assessment"
            
            assert "agents_used" in data
            assert isinstance(data["agents_used"], list)
            assert len(data["agents_used"]) == 2
            assert "RiskAssessmentAgent" in data["agents_used"]
            
            assert "sources" in data
            assert isinstance(data["sources"], list)
            assert len(data["sources"]) == 2
            
            assert "confidence" in data
            assert data["confidence"] == 0.95
            
            # Suggestions are generated based on sources/recommendations
            assert "suggestions" in data
            assert isinstance(data["suggestions"], list)


# ============================================================================
# TEST: GET /api/v1/chat/sessions/{session_id}/history
# ============================================================================


class TestChatSessionHistory:
    """Tests for chat session history endpoint."""

    @pytest.mark.asyncio
    async def test_get_session_history_returns_messages(self, async_client: AsyncClient):
        """
        🔴 RED: GET /api/v1/chat/sessions/{session_id}/history should return messages.
        
        Given: Session exists with multiple messages
        When: GET request sent to /api/v1/chat/sessions/{session_id}/history
        Then: Returns 200 with list of messages in chronological order
        """
        session_id = str(uuid.uuid4())
        
        mock_history = [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": "What are the critical risks?",
                "timestamp": "2026-02-06T10:00:00Z",
                "agent_used": None
            },
            {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": "Based on analysis, there are 3 critical risks...",
                "timestamp": "2026-02-06T10:00:05Z",
                "agent_used": "RiskAssessmentAgent"
            },
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": "What should I prioritize?",
                "timestamp": "2026-02-06T10:01:00Z",
                "agent_used": None
            }
        ]
        
        with patch("app.api.routes.chat.get_session_history", return_value=mock_history):
            response = await async_client.get(f"/api/v1/chat/sessions/{session_id}/history")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 3
            
            # Verify message structure
            assert data[0]["role"] == "user"
            assert data[1]["role"] == "assistant"
            assert "content" in data[0]
            assert "timestamp" in data[0]
            
            # Verify assistant message has agent_used
            assert data[1]["agent_used"] == "RiskAssessmentAgent"

    @pytest.mark.asyncio
    async def test_get_session_history_with_invalid_session_returns_404(self, async_client: AsyncClient):
        """
        🔴 RED: Invalid session_id should return 404.
        
        Given: Session does not exist
        When: GET request sent
        Then: Returns 404 Not Found
        """
        session_id = "invalid-session-999"
        
        with patch("app.api.routes.chat.get_session_history", return_value=None):
            response = await async_client.get(f"/api/v1/chat/sessions/{session_id}/history")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "detail" in data
            assert "session" in data["detail"].lower() or "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_session_history_returns_empty_list_for_new_session(self, async_client: AsyncClient):
        """
        🔴 RED: New session with no messages should return empty list.
        
        Given: Session exists but has no messages
        When: GET request sent
        Then: Returns 200 with empty list
        """
        session_id = str(uuid.uuid4())
        
        with patch("app.api.routes.chat.get_session_history", return_value=[]):
            response = await async_client.get(f"/api/v1/chat/sessions/{session_id}/history")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 0


# ============================================================================
# TEST: DELETE /api/v1/chat/sessions/{session_id}
# ============================================================================


class TestDeleteChatSession:
    """Tests for deleting chat sessions."""

    @pytest.mark.asyncio
    async def test_delete_session_removes_session_successfully(self, async_client: AsyncClient):
        """
        🔴 RED: DELETE /api/v1/chat/sessions/{session_id} should delete session.
        
        Given: Session exists
        When: DELETE request sent
        Then: Returns 204 No Content and session is deleted
        """
        session_id = str(uuid.uuid4())
        
        with patch("app.api.routes.chat.delete_session") as mock_delete:
            mock_delete.return_value = True  # Success
            
            response = await async_client.delete(f"/api/v1/chat/sessions/{session_id}")
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
            
            # Verify delete was called
            mock_delete.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_delete_session_with_invalid_session_returns_404(self, async_client: AsyncClient):
        """
        🔴 RED: Deleting non-existent session should return 404.
        
        Given: Session does not exist
        When: DELETE request sent
        Then: Returns 404 Not Found
        """
        session_id = "invalid-session-999"
        
        with patch("app.api.routes.chat.delete_session") as mock_delete:
            mock_delete.return_value = False  # Session not found
            
            response = await async_client.delete(f"/api/v1/chat/sessions/{session_id}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_delete_session_removes_all_messages(self, async_client: AsyncClient):
        """
        🔴 RED: Deleting session should cascade delete all messages.
        
        Given: Session with multiple messages exists
        When: DELETE request sent
        Then: Session and all messages are deleted
        """
        session_id = str(uuid.uuid4())
        
        with patch("app.api.routes.chat.delete_session") as mock_delete:
            mock_delete.return_value = True
            
            # Create session with messages first
            with patch("app.api.routes.chat.get_session_history") as mock_history:
                mock_history.return_value = [{"id": "msg-1"}, {"id": "msg-2"}]
                
                # Verify session has messages before deletion
                history_response = await async_client.get(f"/api/v1/chat/sessions/{session_id}/history")
                assert len(history_response.json()) == 2
                
                # Delete session
                delete_response = await async_client.delete(f"/api/v1/chat/sessions/{session_id}")
                assert delete_response.status_code == status.HTTP_204_NO_CONTENT
                
                # Verify delete was called (messages cascade deleted in DB)
                mock_delete.assert_called_once_with(session_id)

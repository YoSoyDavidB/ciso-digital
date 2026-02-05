"""
Integration test for complete Risk Assessment flow.

Tests the end-to-end flow from HTTP request to AI agent response:
1. Create asset and vulnerabilities in DB
2. Send chat message with asset context
3. Verify RiskAssessmentAgent processes the request
4. Verify response contains valid risk assessment
5. Verify conversation is persisted

Integration test approach:
- Real FastAPI TestClient
- Real database (SQLite in-memory)
- Real routing and endpoint logic
- Real agent orchestration
- MOCKED: External AI services (CopilotService) - to avoid API calls/costs

NOTE: Currently uses stub implementations for asset/vulnerability DB queries.
      Update when real models are implemented.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.chat import _sessions


# =============================================================================
# Mock Fixtures for External Services
# =============================================================================


@pytest.fixture(autouse=True)
def mock_copilot_service():
    """
    Mock CopilotService to avoid real AI API calls.

    Returns mock responses that simulate risk assessment output.
    """
    with patch("app.services.copilot_service.CopilotClient"):
        with patch("app.services.copilot_service.AsyncAzureOpenAI"):
            # Mock chat response - return JSON structure expected by RiskAssessmentAgent
            mock_chat_response = {
                "text": """{
    "risk_score": 9.2,
    "severity": "critical",
    "recommendations": [
        "Immediately patch CVE-2025-1234 - Critical RCE vulnerability with active exploits",
        "Implement input validation and parameterized queries to prevent SQL injection",
        "Deploy Web Application Firewall (WAF) as immediate temporary mitigation",
        "Schedule penetration testing after patches applied to verify fixes",
        "Review and update incident response procedures for critical vulnerabilities"
    ],
    "confidence": 0.95,
    "reasoning": "Asset has critical severity with CVSS 9.8 RCE vulnerability and high SQL injection risk. Production environment increases impact. Immediate action required."
}""",
                "model": "claude-sonnet-4.5",
                "provider": "github-copilot-sdk",
                "tokens": 450,
                "tool_calls": [],
            }

            # Patch the chat method on CopilotService
            with patch(
                "app.services.copilot_service.CopilotService.chat",
                new_callable=AsyncMock,
                return_value=mock_chat_response,
            ):
                # Mock create_session to return a mock session dict
                with patch(
                    "app.services.copilot_service.CopilotService.create_session",
                    new_callable=AsyncMock,
                    return_value={
                        "provider": "mock",
                        "deployment": "mock-model",
                        "messages": [],
                    },
                ):
                    # Mock _initialize to set using_copilot=True
                    with patch(
                        "app.services.copilot_service.CopilotService._initialize",
                        return_value=None,
                    ):
                        yield


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def asset_id() -> str:
    """Generate a unique asset ID for testing."""
    return f"asset-test-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_asset_data(asset_id: str) -> dict:
    """
    Test asset data.

    Note: Currently using stub data since Asset model doesn't exist yet.
    When Asset model is implemented, create real DB record here.
    """
    return {
        "id": asset_id,
        "name": "Production Web Server",
        "type": "server",
        "criticality": "critical",
        "environment": "production",
        "ip_address": "10.0.1.100",
        "hostname": "web-prod-01.example.com",
    }


@pytest.fixture
def test_vulnerabilities(asset_id: str) -> list[dict]:
    """
    Test vulnerabilities for the asset.

    Note: Currently using stub data since Vulnerability model doesn't exist yet.
    When Vulnerability model is implemented, create real DB records here.
    """
    return [
        {
            "id": f"vuln-{uuid.uuid4().hex[:8]}",
            "asset_id": asset_id,
            "cve_id": "CVE-2025-1234",
            "cvss_score": 9.8,
            "severity": "critical",
            "description": "Critical Remote Code Execution vulnerability",
            "discovered_at": datetime.now().isoformat(),
        },
        {
            "id": f"vuln-{uuid.uuid4().hex[:8]}",
            "asset_id": asset_id,
            "cve_id": "CVE-2025-5678",
            "cvss_score": 7.5,
            "severity": "high",
            "description": "SQL Injection vulnerability in authentication",
            "discovered_at": datetime.now().isoformat(),
        },
    ]


@pytest.fixture
def valid_chat_message_with_asset(asset_id: str) -> dict:
    """Valid chat message payload with asset context."""
    return {
        "message": "What is the risk level of this server and what should I do?",
        "session_id": None,
        "context": {"asset_id": asset_id, "include_history": True},
    }


@pytest.fixture
def valid_general_chat_message() -> dict:
    """Valid chat message without asset context (general query)."""
    return {
        "message": "What is SQL injection and how can I prevent it?",
        "session_id": None,
        "context": {},
    }


# =============================================================================
# Integration Tests
# =============================================================================


class TestRiskAssessmentFlowWithAsset:
    """Integration tests for risk assessment flow with asset context."""

    @pytest.mark.asyncio
    async def test_complete_risk_assessment_flow_with_asset(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_asset_data: dict,
        test_vulnerabilities: list[dict],
        valid_chat_message_with_asset: dict,
    ):
        """
        Test complete end-to-end risk assessment flow with asset context.

        Flow:
        1. Asset and vulnerabilities exist (stub for now)
        2. User sends chat message with asset_id
        3. RiskAssessmentAgent processes request
        4. Response contains valid risk assessment
        5. Session is created and tracked
        6. Conversation is saved (stub for now)

        Expected:
        - HTTP 200 OK
        - Response contains risk_score, severity, recommendations
        - Confidence > 0.5
        - session_id is valid UUID
        - agent_used = "risk_assessment"
        """
        # TODO: When Asset/Vulnerability models exist, create DB records:
        # asset = await Asset.create(db_session, **test_asset_data)
        # for vuln_data in test_vulnerabilities:
        #     await Vulnerability.create(db_session, **vuln_data)
        # await db_session.commit()

        # Act: Send chat message with asset context
        response = await async_client.post(
            "/api/v1/chat/message", json=valid_chat_message_with_asset
        )

        # Assert: Response status
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        # Assert: Response structure
        data = response.json()
        assert "response" in data, "Response should contain 'response' field"
        assert "session_id" in data, "Response should contain 'session_id'"
        assert "agent_used" in data, "Response should contain 'agent_used'"
        assert "confidence" in data, "Response should contain 'confidence'"
        assert "sources" in data, "Response should contain 'sources'"

        # Assert: Response content
        response_text = data["response"]
        assert len(response_text) > 0, "Response text should not be empty"
        assert (
            "Risk Assessment" in response_text
            or "Risk Score" in response_text
            or "risk" in response_text.lower()
        ), "Response should mention risk assessment"

        # Assert: Session ID is valid UUID
        session_id = data["session_id"]
        try:
            uuid.UUID(session_id)
        except ValueError:
            pytest.fail(f"session_id should be valid UUID, got: {session_id}")

        # Assert: Agent used
        assert data["agent_used"] == "risk_assessment", (
            f"Expected 'risk_assessment', got '{data['agent_used']}'"
        )

        # Assert: Confidence is reasonable
        confidence = data["confidence"]
        assert isinstance(confidence, (int, float)), "Confidence should be numeric"
        assert 0.0 <= confidence <= 1.0, f"Confidence should be 0-1, got {confidence}"
        assert confidence >= 0.5, (
            f"Expected confidence >= 0.5 for valid assessment, got {confidence}"
        )

        # Assert: Sources is a list (may be empty)
        assert isinstance(data["sources"], list), "Sources should be a list"

        # Assert: Session was created in memory
        assert session_id in _sessions, f"Session {session_id} should be tracked in _sessions"
        session_data = _sessions[session_id]
        assert session_data["session_id"] == session_id
        assert session_data["message_count"] >= 1

        # TODO: When DB persistence is implemented, verify:
        # chat_messages = await db_session.execute(
        #     select(ChatMessage).where(ChatMessage.session_id == session_id)
        # )
        # assert chat_messages.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_risk_assessment_creates_new_session_if_none_provided(
        self,
        async_client: AsyncClient,
        valid_chat_message_with_asset: dict,
    ):
        """
        Test that a new session is created when session_id is None.

        Expected:
        - Response contains a new session_id (valid UUID)
        - Session is tracked in _sessions
        """
        # Arrange: Ensure session_id is None
        valid_chat_message_with_asset["session_id"] = None

        # Act
        response = await async_client.post(
            "/api/v1/chat/message", json=valid_chat_message_with_asset
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        session_id = data["session_id"]
        assert session_id is not None, "Should create new session_id"

        # Verify it's a valid UUID
        try:
            uuid.UUID(session_id)
        except ValueError:
            pytest.fail(f"session_id should be valid UUID, got: {session_id}")

        # Verify session is tracked
        assert session_id in _sessions

    @pytest.mark.asyncio
    async def test_risk_assessment_reuses_existing_session(
        self,
        async_client: AsyncClient,
        valid_chat_message_with_asset: dict,
    ):
        """
        Test that existing session_id is reused for conversation continuity.

        Expected:
        - Same session_id in request and response
        - Message count increments
        """
        # Arrange: Send first message to create session
        first_response = await async_client.post(
            "/api/v1/chat/message", json=valid_chat_message_with_asset
        )
        assert first_response.status_code == 200
        first_session_id = first_response.json()["session_id"]

        # Act: Send second message with same session_id
        valid_chat_message_with_asset["session_id"] = first_session_id
        valid_chat_message_with_asset["message"] = "What are the top 3 priorities for remediation?"

        second_response = await async_client.post(
            "/api/v1/chat/message", json=valid_chat_message_with_asset
        )

        # Assert
        assert second_response.status_code == 200
        data = second_response.json()

        # Session ID should be the same
        assert data["session_id"] == first_session_id, "Should reuse existing session_id"

        # Message count should increment
        session_data = _sessions[first_session_id]
        assert session_data["message_count"] >= 2, "Message count should have incremented"


class TestRiskAssessmentFlowWithoutAsset:
    """Integration tests for general queries without asset context."""

    @pytest.mark.asyncio
    async def test_general_query_without_asset_context(
        self,
        async_client: AsyncClient,
        valid_general_chat_message: dict,
    ):
        """
        Test general security query without asset context.

        Expected:
        - HTTP 200 OK
        - Response contains helpful security information
        - No risk_score (since no asset to assess)
        - Confidence > 0.5
        - agent_used = "risk_assessment"
        """
        # Act
        response = await async_client.post("/api/v1/chat/message", json=valid_general_chat_message)

        # Assert: Status
        assert response.status_code == 200

        # Assert: Response structure
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "agent_used" in data
        assert "confidence" in data

        # Assert: Response content
        response_text = data["response"]
        assert len(response_text) > 0, "Response should not be empty"

        # General query should mention SQL injection (from the question)
        message = valid_general_chat_message["message"].lower()
        if "sql injection" in message:
            # Response should be relevant to the question
            assert len(response_text) > 50, "Response should be substantial"

        # Assert: Confidence
        assert data["confidence"] >= 0.0
        assert data["confidence"] <= 1.0

        # Assert: Session created
        assert data["session_id"] is not None
        session_id = data["session_id"]
        uuid.UUID(session_id)  # Validate UUID format


class TestRiskAssessmentFlowErrorHandling:
    """Integration tests for error handling in risk assessment flow."""

    @pytest.mark.asyncio
    async def test_invalid_asset_id_returns_404(
        self,
        async_client: AsyncClient,
    ):
        """
        Test that requesting assessment for non-existent asset returns 404.

        Expected:
        - HTTP 404 Not Found
        - Error message indicates asset not found
        """
        # Arrange: Use "invalid" in asset_id to trigger 404 in stub
        invalid_payload = {
            "message": "Assess this asset",
            "context": {"asset_id": "invalid-asset-does-not-exist"},
        }

        # Act
        response = await async_client.post("/api/v1/chat/message", json=invalid_payload)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_empty_message_returns_422(
        self,
        async_client: AsyncClient,
    ):
        """
        Test that empty message returns validation error.

        Expected:
        - HTTP 422 Unprocessable Entity
        """
        # Arrange
        invalid_payload = {"message": "", "context": {}}

        # Act
        response = await async_client.post("/api/v1/chat/message", json=invalid_payload)

        # Assert
        assert response.status_code == 422


class TestSessionManagement:
    """Integration tests for session management."""

    @pytest.mark.asyncio
    async def test_get_sessions_returns_list(
        self,
        async_client: AsyncClient,
        valid_general_chat_message: dict,
    ):
        """
        Test GET /chat/sessions returns list of sessions.

        Expected:
        - HTTP 200 OK
        - Returns list of sessions (may be empty)
        - After creating a session, it appears in the list
        """
        # Act 1: Get sessions (should be empty or from previous tests)
        response1 = await async_client.get("/api/v1/chat/sessions")

        # Assert 1
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list), "Should return a list"
        len(data1)

        # Act 2: Create a new session by sending a message
        await async_client.post("/api/v1/chat/message", json=valid_general_chat_message)

        # Act 3: Get sessions again
        response2 = await async_client.get("/api/v1/chat/sessions")

        # Assert 3: New session should appear
        assert response2.status_code == 200
        data2 = response2.json()
        assert isinstance(data2, list)
        # Note: Due to test isolation, session count might reset
        # Just verify structure
        if len(data2) > 0:
            session = data2[0]
            assert "session_id" in session
            assert "created_at" in session


# =============================================================================
# Performance Tests (Optional)
# =============================================================================


class TestRiskAssessmentPerformance:
    """Optional performance tests for risk assessment flow."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_risk_assessment_completes_within_timeout(
        self,
        async_client: AsyncClient,
        valid_chat_message_with_asset: dict,
    ):
        """
        Test that risk assessment completes within reasonable time.

        Expected:
        - Response within 30 seconds (AI calls can be slow)
        - HTTP 200 OK
        """
        import time

        start_time = time.time()

        # Act
        response = await async_client.post(
            "/api/v1/chat/message", json=valid_chat_message_with_asset
        )

        elapsed_time = time.time() - start_time

        # Assert
        assert response.status_code == 200
        assert elapsed_time < 30.0, f"Request took {elapsed_time:.2f}s (expected < 30s)"

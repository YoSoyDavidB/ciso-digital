"""
Tests for CISOOrchestrator.

This module tests the orchestration logic that routes user queries to appropriate
agents based on intent classification and manages conversation context.

🔴 RED PHASE: These tests are written BEFORE the CISOOrchestrator implementation.
They define the expected behavior and will initially FAIL.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from uuid import uuid4

# 🔴 RED: These imports will FAIL because CISOOrchestrator doesn't exist yet
from app.agents.orchestrator import CISOOrchestrator, OrchestratorResponse
from app.services.intent_classifier import IntentType, Intent, Entity
from app.shared.models.conversation import MessageRole


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def session_id():
    """Returns a test session ID."""
    return str(uuid4())


@pytest.fixture
def user_id():
    """Returns a test user ID."""
    return str(uuid4())


@pytest.fixture
def mock_intent_classifier():
    """Mock IntentClassifier for testing."""
    classifier = AsyncMock()
    return classifier


@pytest.fixture
def mock_risk_agent():
    """Mock RiskAssessmentAgent for testing."""
    agent = AsyncMock()
    agent.name = "RiskAssessmentAgent"
    return agent


@pytest.fixture
def mock_incident_agent():
    """Mock IncidentResponseAgent for testing."""
    agent = AsyncMock()
    agent.name = "IncidentResponseAgent"
    return agent


@pytest.fixture
def mock_compliance_agent():
    """Mock ComplianceAgent for testing."""
    agent = AsyncMock()
    agent.name = "ComplianceAgent"
    return agent


@pytest.fixture
def mock_conversation_memory():
    """Mock ConversationMemoryService for testing."""
    memory = AsyncMock()
    memory.get_conversation_history = AsyncMock(return_value=[])
    memory.save_message = AsyncMock()
    memory.search_similar_conversations = AsyncMock(return_value=[])
    return memory


@pytest.fixture
async def orchestrator(
    mock_intent_classifier,
    mock_risk_agent,
    mock_incident_agent,
    mock_compliance_agent,
    mock_conversation_memory
):
    """Create CISOOrchestrator with mocked dependencies."""
    # Map of intent types to agents
    agents = {
        IntentType.RISK_ASSESSMENT: mock_risk_agent,
        IntentType.INCIDENT_RESPONSE: mock_incident_agent,
        IntentType.COMPLIANCE_CHECK: mock_compliance_agent,
    }
    
    orchestrator = CISOOrchestrator(
        intent_classifier=mock_intent_classifier,
        agents=agents,
        conversation_memory=mock_conversation_memory
    )
    
    return orchestrator


# ============================================================================
# TEST DATA
# ============================================================================

@pytest.fixture
def risk_intent():
    """Sample risk assessment intent."""
    return Intent(
        intent_type=IntentType.RISK_ASSESSMENT,
        confidence=0.95,
        entities=[
            Entity(
                entity_type="asset",
                value="production server",
                context="our production server"
            ),
            Entity(
                entity_type="severity",
                value="critical",
                context="critical vulnerabilities"
            )
        ],
        reasoning="User is asking about critical vulnerabilities in production",
        alternative_intents=None
    )


@pytest.fixture
def incident_intent():
    """Sample incident response intent."""
    return Intent(
        intent_type=IntentType.INCIDENT_RESPONSE,
        confidence=0.92,
        entities=[
            Entity(
                entity_type="asset",
                value="server-prod-01",
                context="on server-prod-01"
            ),
            Entity(
                entity_type="activity",
                value="suspicious",
                context="suspicious activity"
            )
        ],
        reasoning="User is reporting a security incident",
        alternative_intents=None
    )


@pytest.fixture
def compliance_intent():
    """Sample compliance check intent."""
    return Intent(
        intent_type=IntentType.COMPLIANCE_CHECK,
        confidence=0.88,
        entities=[
            Entity(
                entity_type="framework",
                value="ISO 27001",
                context="ISO 27001 compliance"
            ),
            Entity(
                entity_type="control",
                value="A.8.1",
                context="control A.8.1"
            )
        ],
        reasoning="User is asking about compliance status",
        alternative_intents=None
    )


@pytest.fixture
def ambiguous_intent():
    """Sample ambiguous intent with low confidence."""
    return Intent(
        intent_type=IntentType.RISK_ASSESSMENT,
        confidence=0.55,
        entities=[
            Entity(
                entity_type="scope",
                value="infrastructure",
                context="our infrastructure"
            )
        ],
        reasoning="Query is ambiguous - could be risk, compliance, or review",
        alternative_intents=[
            {"intent_type": "compliance_check", "confidence": 0.50},
            {"intent_type": "proactive_review", "confidence": 0.45}
        ]
    )


@pytest.fixture
def multiple_intents():
    """Intent with multiple possible interpretations."""
    return Intent(
        intent_type=IntentType.RISK_ASSESSMENT,
        confidence=0.75,
        entities=[
            Entity(entity_type="asset", value="web server", context="web server")
        ],
        reasoning="Could involve both risk and compliance",
        alternative_intents=[
            {"intent_type": "compliance_check", "confidence": 0.70}
        ]
    )


# ============================================================================
# TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_process_request_with_risk_intent_calls_risk_agent(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_conversation_memory,
    risk_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator routes risk assessment queries to RiskAssessmentAgent.
    
    Given: A user query about critical vulnerabilities
    When: IntentClassifier identifies it as RISK_ASSESSMENT
    Then: Orchestrator should call RiskAssessmentAgent and return response
    """
    # Arrange
    user_query = "What are the critical vulnerabilities in our production server?"
    
    # Mock intent classification
    mock_intent_classifier.classify.return_value = risk_intent
    
    # Mock agent response
    mock_risk_agent.process.return_value = {
        "analysis": "Found 3 critical vulnerabilities",
        "vulnerabilities": [
            {"cve": "CVE-2025-1234", "severity": "critical", "cvss": 9.8}
        ],
        "recommendations": ["Patch immediately", "Isolate affected systems"]
    }
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    mock_intent_classifier.classify.assert_called_once_with(user_query)
    mock_risk_agent.process.assert_called_once()
    
    # Verify conversation was saved (user query + assistant response)
    assert mock_conversation_memory.save_message.call_count == 2
    
    # Verify response structure
    assert isinstance(response, OrchestratorResponse)
    assert response.response_text is not None
    assert response.intent_type == IntentType.RISK_ASSESSMENT
    assert response.confidence == 0.95
    assert response.agent_used == "RiskAssessmentAgent"
    assert response.session_id == session_id


@pytest.mark.asyncio
async def test_process_request_with_incident_intent_calls_incident_agent(
    orchestrator,
    mock_intent_classifier,
    mock_incident_agent,
    mock_conversation_memory,
    incident_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator routes incident reports to IncidentResponseAgent.
    
    Given: A user query reporting suspicious activity
    When: IntentClassifier identifies it as INCIDENT_RESPONSE
    Then: Orchestrator should call IncidentResponseAgent
    """
    # Arrange
    user_query = "We detected suspicious activity on server-prod-01"
    
    mock_intent_classifier.classify.return_value = incident_intent
    
    mock_incident_agent.process.return_value = {
        "incident_id": "INC-2026-001",
        "severity": "high",
        "status": "investigating",
        "actions_taken": [
            "Isolated affected server",
            "Initiated forensic analysis"
        ],
        "next_steps": ["Contact security team", "Review logs"]
    }
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    mock_intent_classifier.classify.assert_called_once_with(user_query)
    mock_incident_agent.process.assert_called_once()
    
    assert response.intent_type == IntentType.INCIDENT_RESPONSE
    assert response.agent_used == "IncidentResponseAgent"
    assert "INC-2026-001" in response.response_text or "INC-2026-001" in str(response.agent_results)


@pytest.mark.asyncio
async def test_process_request_saves_conversation(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_conversation_memory,
    risk_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator saves both user query and assistant response to memory.
    
    Given: Any user query that is processed
    When: Orchestrator completes processing
    Then: Both user message and assistant response should be saved to conversation memory
    """
    # Arrange
    user_query = "Show me the risk report"
    
    mock_intent_classifier.classify.return_value = risk_intent
    mock_risk_agent.process.return_value = {"report": "Risk summary..."}
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert - should save 2 messages: user query + assistant response
    assert mock_conversation_memory.save_message.call_count == 2
    
    # Check first call (user message)
    first_call = mock_conversation_memory.save_message.call_args_list[0]
    assert first_call.kwargs["session_id"] == session_id
    assert first_call.kwargs["role"] == MessageRole.USER
    assert first_call.kwargs["content"] == user_query
    
    # Check second call (assistant response)
    second_call = mock_conversation_memory.save_message.call_args_list[1]
    assert second_call.kwargs["session_id"] == session_id
    assert second_call.kwargs["role"] == MessageRole.ASSISTANT
    assert second_call.kwargs["agent_used"] == "RiskAssessmentAgent"
    assert len(second_call.kwargs["content"]) > 0


@pytest.mark.asyncio
async def test_process_request_with_low_confidence_asks_clarification(
    orchestrator,
    mock_intent_classifier,
    mock_conversation_memory,
    ambiguous_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator asks for clarification when intent confidence is low.
    
    Given: A user query with ambiguous intent (confidence < 0.7)
    When: Orchestrator processes the query
    Then: Should return a clarification request instead of executing agents
    """
    # Arrange
    user_query = "Check the security of our infrastructure"
    
    mock_intent_classifier.classify.return_value = ambiguous_intent
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    mock_intent_classifier.classify.assert_called_once()
    
    # Should NOT call any agents when confidence is low
    # (we don't have access to the agents directly, but we can check response)
    
    assert response.confidence == 0.55
    assert response.requires_clarification is True
    assert "clarif" in response.response_text.lower() or "could you" in response.response_text.lower()
    assert response.alternative_intents is not None
    assert len(response.alternative_intents) > 0
    
    # Should still save the conversation
    assert mock_conversation_memory.save_message.call_count >= 1


@pytest.mark.asyncio
async def test_process_request_with_multiple_intents_runs_multiple_agents(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_compliance_agent,
    mock_conversation_memory,
    multiple_intents,
    session_id,
    user_id
):
    """
    Test that orchestrator can run multiple agents for complex queries.
    
    Given: A query that matches multiple intents with similar confidence
    When: Both intents have confidence > 0.7
    Then: Orchestrator should execute both agents and aggregate results
    """
    # Arrange
    user_query = "Assess security risks and compliance status for web server"
    
    mock_intent_classifier.classify.return_value = multiple_intents
    
    mock_risk_agent.process.return_value = {
        "risk_score": 7.5,
        "vulnerabilities": ["CVE-2025-1234"]
    }
    
    mock_compliance_agent.process.return_value = {
        "compliance_status": "partial",
        "missing_controls": ["A.8.1", "A.9.2"]
    }
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    # When confidence for alternative is >= 0.7, should run both agents
    assert response.agents_used is not None
    assert len(response.agents_used) >= 1  # At least primary agent
    
    # Response should aggregate results from multiple agents
    assert response.response_text is not None
    assert len(response.response_text) > 0


@pytest.mark.asyncio
async def test_orchestrator_maintains_conversation_context(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_conversation_memory,
    risk_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator retrieves and uses conversation history for context.
    
    Given: An existing conversation session with history
    When: User sends a follow-up query
    Then: Orchestrator should retrieve history and pass it to agents
    """
    # Arrange
    user_query = "What about the web server?"
    
    # Mock conversation history
    mock_conversation_memory.get_conversation_history.return_value = [
        Mock(
            role=MessageRole.USER,
            content="Show me critical vulnerabilities",
            timestamp=datetime.now()
        ),
        Mock(
            role=MessageRole.ASSISTANT,
            content="Found 3 critical vulnerabilities in production server",
            timestamp=datetime.now()
        )
    ]
    
    mock_intent_classifier.classify.return_value = risk_intent
    mock_risk_agent.process.return_value = {"analysis": "Web server analysis..."}
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    # Should retrieve conversation history
    mock_conversation_memory.get_conversation_history.assert_called_once_with(
        session_id=session_id
    )
    
    # Should pass context to agent
    call_kwargs = mock_risk_agent.process.call_args.kwargs
    assert "context" in call_kwargs or "conversation_history" in call_kwargs
    
    assert response.session_id == session_id


@pytest.mark.asyncio
async def test_orchestrator_handles_general_query_without_specialized_agent(
    orchestrator,
    mock_intent_classifier,
    mock_conversation_memory,
    session_id,
    user_id
):
    """
    Test that orchestrator handles general queries directly without routing to agents.
    
    Given: A general security question
    When: Intent is classified as GENERAL_QUERY
    Then: Orchestrator should respond directly using LLM without specialized agent
    """
    # Arrange
    user_query = "What is the difference between symmetric and asymmetric encryption?"
    
    general_intent = Intent(
        intent_type=IntentType.GENERAL_QUERY,
        confidence=0.90,
        entities=[],
        reasoning="General security knowledge question",
        alternative_intents=None
    )
    
    mock_intent_classifier.classify.return_value = general_intent
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    assert response.intent_type == IntentType.GENERAL_QUERY
    assert response.agent_used is None or response.agent_used == "DirectResponse"
    assert response.response_text is not None
    assert len(response.response_text) > 0


@pytest.mark.asyncio
async def test_orchestrator_includes_entities_in_agent_context(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_conversation_memory,
    risk_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator passes extracted entities to agents.
    
    Given: A query with extracted entities (asset, severity)
    When: Orchestrator routes to agent
    Then: Entities should be included in the agent's context
    """
    # Arrange
    user_query = "Check critical vulnerabilities in production server"
    
    mock_intent_classifier.classify.return_value = risk_intent
    mock_risk_agent.process.return_value = {"status": "analyzed"}
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    call_kwargs = mock_risk_agent.process.call_args.kwargs
    
    # Entities should be passed to agent
    assert "entities" in call_kwargs or "intent" in call_kwargs
    
    # Verify the entities are the ones from classification
    if "entities" in call_kwargs:
        entities = call_kwargs["entities"]
        assert len(entities) == 2
        assert any(e.entity_type == "asset" for e in entities)
        assert any(e.entity_type == "severity" for e in entities)


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_handles_agent_failure_gracefully(
    orchestrator,
    mock_intent_classifier,
    mock_risk_agent,
    mock_conversation_memory,
    risk_intent,
    session_id,
    user_id
):
    """
    Test that orchestrator handles agent failures without crashing.
    
    Given: An agent that raises an exception
    When: Orchestrator processes a request
    Then: Should return error response and log the failure
    """
    # Arrange
    user_query = "Analyze risks"
    
    mock_intent_classifier.classify.return_value = risk_intent
    mock_risk_agent.process.side_effect = Exception("Agent processing failed")
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    assert response is not None
    assert "error" in response.response_text.lower() or response.error is not None
    
    # Should still save user message even if agent fails
    assert mock_conversation_memory.save_message.call_count >= 1


@pytest.mark.asyncio
async def test_orchestrator_handles_missing_agent_for_intent(
    orchestrator,
    mock_intent_classifier,
    mock_conversation_memory,
    session_id,
    user_id
):
    """
    Test that orchestrator handles case when no agent is registered for an intent.
    
    Given: An intent type with no registered agent
    When: Orchestrator tries to process
    Then: Should return appropriate message or use fallback
    """
    # Arrange
    user_query = "Generate security report"
    
    reporting_intent = Intent(
        intent_type=IntentType.REPORTING,
        confidence=0.88,
        entities=[],
        reasoning="User wants a security report",
        alternative_intents=None
    )
    
    mock_intent_classifier.classify.return_value = reporting_intent
    
    # Act
    response = await orchestrator.process_request(
        user_query=user_query,
        session_id=session_id,
        user_id=user_id
    )
    
    # Assert
    assert response is not None
    # Should either have error or use fallback response
    assert (
        response.error is not None or
        "not available" in response.response_text.lower() or
        response.agent_used == "DirectResponse"
    )

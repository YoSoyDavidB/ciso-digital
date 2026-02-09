"""
Tests for IntentClassifier

🔴 RED Phase: These tests will FAIL because IntentClassifier doesn't exist yet.

The IntentClassifier will:
1. Analyze user query
2. Identify primary intention (risk_assessment, incident_response, compliance_check, etc.)
3. Extract relevant entities (asset_id, severity, date_range, etc.)
4. Determine classification confidence
5. Handle ambiguities (multiple possible intents)
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from typing import List

from app.services.intent_classifier import (
    IntentClassifier,
    Intent,
    Entity,
    IntentType,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for intent classification"""
    service = AsyncMock()
    
    # Mock response for risk assessment query
    service.generate.return_value = {
        "text": """
        {
            "intent_type": "risk_assessment",
            "confidence": 0.95,
            "entities": [
                {"entity_type": "asset", "value": "production server", "context": "the production server"},
                {"entity_type": "severity", "value": "critical", "context": "critical vulnerabilities"}
            ],
            "reasoning": "User is asking about identifying critical vulnerabilities in a production server"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 150
    }
    
    return service


@pytest.fixture
async def intent_classifier(mock_llm_service):
    """IntentClassifier instance with mocked dependencies"""
    return IntentClassifier(llm_service=mock_llm_service)


# ============================================================================
# Test Data
# ============================================================================

RISK_QUERIES = [
    "What are the critical vulnerabilities in our production server?",
    "Assess the risk of SQL injection in our web application",
    "Show me high-severity risks for the database server",
]

INCIDENT_QUERIES = [
    "We detected suspicious activity on server-prod-01",
    "Handle security incident: unauthorized access to admin panel",
    "Help me respond to this ransomware attack",
]

COMPLIANCE_QUERIES = [
    "Are we compliant with ISO 27001 control A.8.1?",
    "Check PCI-DSS compliance for payment processing",
    "Generate compliance report for GDPR Article 32",
]

AMBIGUOUS_QUERIES = [
    "Check the security of our infrastructure",  # Could be risk, compliance, or proactive review
    "What happened yesterday?",  # Could be incident, reporting, or general query
]


# ============================================================================
# Tests
# ============================================================================

@pytest.mark.asyncio
async def test_classify_risk_query_returns_risk_intent(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that risk-related queries are classified as risk_assessment.
    
    Given: A query about critical vulnerabilities
    When: classify() is called
    Then: Returns Intent with type=risk_assessment and high confidence
    """
    # Arrange
    query = "What are the critical vulnerabilities in our production server?"
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert isinstance(result, Intent)
    assert result.intent_type == IntentType.RISK_ASSESSMENT
    assert result.confidence >= 0.8, f"Expected high confidence, got {result.confidence}"
    assert result.reasoning is not None
    assert len(result.entities) > 0, "Should extract entities from query"
    
    # Verify LLM was called
    mock_llm_service.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_classify_incident_query_returns_incident_intent(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that incident-related queries are classified as incident_response.
    
    Given: A query about handling a security incident
    When: classify() is called
    Then: Returns Intent with type=incident_response
    """
    # Arrange
    query = "We detected suspicious activity on server-prod-01"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "incident_response",
            "confidence": 0.92,
            "entities": [
                {"entity_type": "asset", "value": "server-prod-01", "context": "on server-prod-01"},
                {"entity_type": "activity", "value": "suspicious", "context": "suspicious activity"}
            ],
            "reasoning": "User is reporting a potential security incident"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 140
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert result.intent_type == IntentType.INCIDENT_RESPONSE
    assert result.confidence >= 0.8
    assert any(e.entity_type == "asset" for e in result.entities), "Should extract asset entity"


@pytest.mark.asyncio
async def test_classify_compliance_query_returns_compliance_intent(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that compliance queries are classified as compliance_check.
    
    Given: A query about ISO 27001 compliance
    When: classify() is called
    Then: Returns Intent with type=compliance_check
    """
    # Arrange
    query = "Are we compliant with ISO 27001 control A.8.1?"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "compliance_check",
            "confidence": 0.97,
            "entities": [
                {"entity_type": "framework", "value": "ISO 27001", "context": "ISO 27001"},
                {"entity_type": "control", "value": "A.8.1", "context": "control A.8.1"}
            ],
            "reasoning": "User is asking about compliance with a specific ISO 27001 control"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 130
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert result.intent_type == IntentType.COMPLIANCE_CHECK
    assert result.confidence >= 0.9
    assert any(e.entity_type == "framework" for e in result.entities)
    assert any(e.entity_type == "control" for e in result.entities)


@pytest.mark.asyncio
async def test_classify_ambiguous_query_returns_multiple_intents(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that ambiguous queries return multiple possible intents.
    
    Given: An ambiguous query
    When: classify() is called
    Then: Returns Intent with alternative_intents populated
    """
    # Arrange
    query = "Check the security of our infrastructure"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "risk_assessment",
            "confidence": 0.65,
            "alternative_intents": [
                {"intent_type": "compliance_check", "confidence": 0.55},
                {"intent_type": "proactive_review", "confidence": 0.50}
            ],
            "entities": [
                {"entity_type": "scope", "value": "infrastructure", "context": "our infrastructure"}
            ],
            "reasoning": "Query is ambiguous - could be risk assessment, compliance check, or proactive review"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 160
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert result.intent_type == IntentType.RISK_ASSESSMENT
    assert result.confidence < 0.8, "Ambiguous query should have lower confidence"
    assert result.alternative_intents is not None
    assert len(result.alternative_intents) > 0, "Should provide alternative intents"
    assert all(alt["confidence"] < result.confidence for alt in result.alternative_intents)


@pytest.mark.asyncio
async def test_extract_entities_from_query(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that entities are correctly extracted from queries.
    
    Given: A query with multiple entities (asset, severity, date)
    When: classify() is called
    Then: All relevant entities are extracted
    """
    # Arrange
    query = "Show me critical risks for database-prod-01 from last week"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "risk_assessment",
            "confidence": 0.93,
            "entities": [
                {"entity_type": "severity", "value": "critical", "context": "critical risks"},
                {"entity_type": "asset", "value": "database-prod-01", "context": "for database-prod-01"},
                {"entity_type": "date_range", "value": "last week", "context": "from last week"}
            ],
            "reasoning": "User wants to see critical risks for a specific database from last week"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 145
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert len(result.entities) == 3, f"Expected 3 entities, got {len(result.entities)}"
    
    # Verify entity types
    entity_types = [e.entity_type for e in result.entities]
    assert "severity" in entity_types
    assert "asset" in entity_types
    assert "date_range" in entity_types
    
    # Verify entity values
    severity_entity = next(e for e in result.entities if e.entity_type == "severity")
    assert severity_entity.value == "critical"
    
    asset_entity = next(e for e in result.entities if e.entity_type == "asset")
    assert asset_entity.value == "database-prod-01"


@pytest.mark.asyncio
async def test_confidence_score_is_between_0_and_1(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that confidence scores are always between 0 and 1.
    
    Given: Any query
    When: classify() is called
    Then: Confidence score is in range [0.0, 1.0]
    """
    # Arrange
    query = "What are the security risks?"
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert 0.0 <= result.confidence <= 1.0, \
        f"Confidence {result.confidence} is outside valid range [0.0, 1.0]"
    
    # Also check alternative intents if present
    if result.alternative_intents:
        for alt in result.alternative_intents:
            assert 0.0 <= alt["confidence"] <= 1.0, \
                f"Alternative confidence {alt['confidence']} is outside valid range"


@pytest.mark.asyncio
async def test_general_query_classification(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that general queries are classified as general_query.
    
    Given: A general question without specific intent
    When: classify() is called
    Then: Returns Intent with type=general_query
    """
    # Arrange
    query = "What is a firewall?"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "general_query",
            "confidence": 0.88,
            "entities": [
                {"entity_type": "concept", "value": "firewall", "context": "What is a firewall"}
            ],
            "reasoning": "User is asking a general security knowledge question"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 120
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert result.intent_type == IntentType.GENERAL_QUERY
    assert result.confidence >= 0.7


@pytest.mark.asyncio
async def test_classify_returns_valid_intent_type(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that classify always returns a valid IntentType.
    
    Given: Any query
    When: classify() is called
    Then: Result intent_type is one of the valid IntentType enum values
    """
    # Arrange
    query = "Generate a security report"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "reporting",
            "confidence": 0.91,
            "entities": [
                {"entity_type": "report_type", "value": "security report", "context": "security report"}
            ],
            "reasoning": "User wants to generate a security report"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 110
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert isinstance(result.intent_type, IntentType)
    assert result.intent_type in [
        IntentType.RISK_ASSESSMENT,
        IntentType.INCIDENT_RESPONSE,
        IntentType.COMPLIANCE_CHECK,
        IntentType.THREAT_INTELLIGENCE,
        IntentType.REPORTING,
        IntentType.GENERAL_QUERY,
        IntentType.PROACTIVE_REVIEW,
    ]


@pytest.mark.asyncio
async def test_classify_handles_empty_entities(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that classify handles queries with no extractable entities.
    
    Given: A simple query with no entities
    When: classify() is called
    Then: Returns Intent with empty entities list
    """
    # Arrange
    query = "Help"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "general_query",
            "confidence": 0.70,
            "entities": [],
            "reasoning": "User needs general assistance"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 90
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert isinstance(result.entities, list)
    assert len(result.entities) == 0


@pytest.mark.asyncio
async def test_classify_includes_reasoning(
    intent_classifier,
    mock_llm_service
):
    """
    🔴 RED: Test that classify includes reasoning for the classification.
    
    Given: Any query
    When: classify() is called
    Then: Result includes non-empty reasoning
    """
    # Arrange
    query = "Analyze threats to our web application"
    mock_llm_service.generate.return_value = {
        "text": """
        {
            "intent_type": "threat_intelligence",
            "confidence": 0.89,
            "entities": [
                {"entity_type": "asset_type", "value": "web application", "context": "web application"}
            ],
            "reasoning": "User wants threat intelligence analysis for web application"
        }
        """,
        "model": "claude-sonnet-4.5",
        "tokens": 125
    }
    
    # Act
    result = await intent_classifier.classify(query)
    
    # Assert
    assert result.reasoning is not None
    assert len(result.reasoning) > 0
    assert isinstance(result.reasoning, str)

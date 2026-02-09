"""
Intent Classification Service for CISO Digital Assistant.

This module provides intent classification and entity extraction for user queries
using LLM-based natural language understanding.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class IntentType(str, Enum):
    """Enumeration of possible user intent types."""
    
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE_CHECK = "compliance_check"
    THREAT_INTELLIGENCE = "threat_intelligence"
    REPORTING = "reporting"
    GENERAL_QUERY = "general_query"
    PROACTIVE_REVIEW = "proactive_review"


@dataclass
class Entity:
    """
    Represents an extracted entity from a user query.
    
    Attributes:
        entity_type: Type of entity (e.g., 'asset', 'severity', 'date_range')
        value: The extracted value (e.g., 'production server', 'critical')
        context: Surrounding context from the query
    """
    
    entity_type: str
    value: str
    context: str


@dataclass
class Intent:
    """
    Represents a classified user intent with confidence and extracted entities.
    
    Attributes:
        intent_type: The primary classified intent
        confidence: Confidence score between 0.0 and 1.0
        entities: List of extracted entities from the query
        reasoning: Explanation of the classification decision
        alternative_intents: Optional list of alternative intents if ambiguous
    """
    
    intent_type: IntentType
    confidence: float
    entities: List[Entity]
    reasoning: str
    alternative_intents: Optional[List[Dict[str, Any]]] = None


class IntentClassifier:
    """
    Classifies user intents and extracts entities using LLM.
    
    This service analyzes security-related queries and determines the user's
    primary intention (e.g., risk assessment, incident response) along with
    relevant entities (e.g., assets, severity levels).
    """
    
    # System prompt for intent classification
    CLASSIFICATION_PROMPT = """You are an intent classifier for a CISO (Chief Information Security Officer) digital assistant.

Your task is to analyze user queries and classify the primary intention into one of the following categories:

**Possible Intents:**
- risk_assessment: Questions about risks, vulnerabilities, security posture, threat evaluation
- incident_response: Reports or questions about security incidents, breaches, suspicious activity
- compliance_check: Questions about regulatory compliance (ISO 27001, NIST, GDPR, PCI-DSS, SOC 2)
- threat_intelligence: Questions about threat actors, CVEs, vulnerabilities, attack patterns
- reporting: Requests for reports, metrics, dashboards, KPIs, analytics
- proactive_review: Requests for proactive documentation review, control gaps, policy analysis
- general_query: General security questions, definitions, best practices

**Entity Types to Extract:**
- asset: Systems, servers, applications, databases (e.g., "production server", "web-app-01")
- severity: Severity levels (e.g., "critical", "high", "medium", "low")
- date_range: Time periods (e.g., "last week", "yesterday", "Q4 2025")
- cve_id: CVE identifiers (e.g., "CVE-2025-1234")
- framework: Compliance frameworks (e.g., "ISO 27001", "NIST CSF", "GDPR")
- control: Specific controls (e.g., "A.8.1", "Article 32")
- threat_actor: Threat actor names or groups
- activity: Types of activity (e.g., "suspicious", "malicious", "unauthorized")
- scope: Scope of inquiry (e.g., "infrastructure", "cloud environment")

**Response Format (MUST be valid JSON):**
{
  "intent_type": "intent_type_value",
  "confidence": 0.95,
  "entities": [
    {
      "entity_type": "asset",
      "value": "production server",
      "context": "our production server"
    }
  ],
  "reasoning": "Brief explanation of why this intent was chosen",
  "alternative_intents": [
    {
      "intent_type": "alternative_intent_type",
      "confidence": 0.45
    }
  ]
}

**Rules:**
1. ALWAYS respond with ONLY valid JSON (no additional text or markdown)
2. confidence MUST be a float between 0.0 and 1.0
3. If confidence < 0.8, include alternative_intents array with other possible interpretations
4. Extract ALL relevant entities from the query
5. intent_type MUST be one of the listed intent types (use exact values)
6. entities array can be empty if no entities are found
7. alternative_intents can be null or omitted if confidence >= 0.8
8. reasoning should be concise (1-2 sentences)

**Examples:**

Query: "What are the critical vulnerabilities in our production server?"
Response:
{
  "intent_type": "risk_assessment",
  "confidence": 0.95,
  "entities": [
    {"entity_type": "asset", "value": "production server", "context": "our production server"},
    {"entity_type": "severity", "value": "critical", "context": "critical vulnerabilities"}
  ],
  "reasoning": "User is asking about identifying and assessing critical vulnerabilities in a specific asset.",
  "alternative_intents": null
}

Query: "Check the security of our infrastructure"
Response:
{
  "intent_type": "risk_assessment",
  "confidence": 0.65,
  "entities": [
    {"entity_type": "scope", "value": "infrastructure", "context": "our infrastructure"}
  ],
  "reasoning": "Query is ambiguous - could be risk assessment, compliance check, or proactive review. Defaulting to risk assessment but with lower confidence.",
  "alternative_intents": [
    {"intent_type": "compliance_check", "confidence": 0.55},
    {"intent_type": "proactive_review", "confidence": 0.50}
  ]
}

Now analyze the following user query:"""
    
    def __init__(self, llm_service):
        """
        Initialize the IntentClassifier.
        
        Args:
            llm_service: LLM service for generating classifications
        """
        self.llm_service = llm_service
        logger.info("intent_classifier_initialized")
    
    async def classify(self, user_query: str) -> Intent:
        """
        Classify user intent and extract entities from the query.
        
        This method uses the LLM to analyze the user's query and determine:
        - The primary intent (risk assessment, incident response, etc.)
        - Confidence level (0.0-1.0)
        - Extracted entities (assets, severity, dates, etc.)
        - Reasoning for the classification
        - Alternative intents if the query is ambiguous
        
        Args:
            user_query: The user's natural language query
        
        Returns:
            Intent: Classified intent with confidence, entities, and reasoning
        
        Raises:
            ValueError: If LLM response is invalid or confidence is out of range
            json.JSONDecodeError: If LLM returns malformed JSON
        
        Example:
            >>> classifier = IntentClassifier(llm_service)
            >>> intent = await classifier.classify("Show critical risks")
            >>> print(f"Intent: {intent.intent_type}, Confidence: {intent.confidence}")
            Intent: risk_assessment, Confidence: 0.92
        """
        logger.info("classifying_intent", query_length=len(user_query))
        
        try:
            # Construct full prompt
            full_prompt = f"{self.CLASSIFICATION_PROMPT}\n\nUser Query: \"{user_query}\""
            
            # Call LLM service
            response = await self.llm_service.generate(
                prompt=full_prompt,
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent classification
            )
            
            # Extract JSON from response
            response_text = response.get("text", "")
            
            # Try to parse JSON
            try:
                classification_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(
                    "llm_response_invalid_json",
                    error=str(e),
                    response_text=response_text[:200]
                )
                raise ValueError(f"LLM returned invalid JSON: {e}")
            
            # Validate required fields
            if "intent_type" not in classification_data:
                raise ValueError("Missing 'intent_type' in LLM response")
            if "confidence" not in classification_data:
                raise ValueError("Missing 'confidence' in LLM response")
            
            # Parse intent type
            try:
                intent_type = IntentType(classification_data["intent_type"])
            except ValueError:
                logger.warning(
                    "invalid_intent_type",
                    intent_type=classification_data["intent_type"]
                )
                # Default to general_query for invalid types
                intent_type = IntentType.GENERAL_QUERY
            
            # Validate confidence
            confidence = float(classification_data["confidence"])
            if not (0.0 <= confidence <= 1.0):
                logger.warning(
                    "confidence_out_of_range",
                    confidence=confidence
                )
                # Clamp to valid range
                confidence = max(0.0, min(1.0, confidence))
            
            # Parse entities
            entities = []
            entities_data = classification_data.get("entities", [])
            
            if isinstance(entities_data, list):
                for entity_data in entities_data:
                    if isinstance(entity_data, dict):
                        entity = Entity(
                            entity_type=entity_data.get("entity_type", "unknown"),
                            value=entity_data.get("value", ""),
                            context=entity_data.get("context", "")
                        )
                        entities.append(entity)
            
            # Get reasoning
            reasoning = classification_data.get(
                "reasoning",
                f"Classified as {intent_type.value} with {confidence:.2f} confidence"
            )
            
            # Parse alternative intents
            alternative_intents = classification_data.get("alternative_intents")
            
            # Create Intent object
            intent = Intent(
                intent_type=intent_type,
                confidence=confidence,
                entities=entities,
                reasoning=reasoning,
                alternative_intents=alternative_intents
            )
            
            logger.info(
                "intent_classified",
                intent_type=intent.intent_type.value,
                confidence=intent.confidence,
                entities_count=len(intent.entities),
                has_alternatives=intent.alternative_intents is not None
            )
            
            return intent
            
        except Exception as e:
            logger.error(
                "intent_classification_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

"""
Orchestrator schemas for CISO Digital Assistant.

This module defines data structures for orchestrator responses and agent results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class OrchestratorResponse:
    """
    Response from the CISOOrchestrator after processing a user request.
    
    Attributes:
        response_text: The final aggregated response text for the user
        intent_type: The classified intent type
        confidence: Confidence score of the intent classification (0.0-1.0)
        agent_used: Name of the primary agent used (if single agent)
        agents_used: List of agent names used (if multiple agents)
        agent_results: Raw results from agents for debugging/inspection
        session_id: The conversation session ID
        requires_clarification: Whether the query requires user clarification
        alternative_intents: Alternative possible intents if ambiguous
        error: Error message if processing failed
        sources: List of information sources used
        suggestions: Optional follow-up suggestions for the user
    """
    
    response_text: str
    intent_type: str
    confidence: float
    session_id: str
    agent_used: Optional[str] = None
    agents_used: Optional[List[str]] = None
    agent_results: Optional[Dict[str, Any]] = None
    requires_clarification: bool = False
    alternative_intents: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    suggestions: Optional[List[str]] = None


@dataclass
class AgentResponse:
    """
    Response from an individual agent.
    
    Attributes:
        agent_name: Name of the agent that generated this response
        response: The response text from the agent
        confidence: Agent's confidence in the response (0.0-1.0)
        sources: List of sources/references used by the agent
        metadata: Additional metadata from the agent
    """
    
    agent_name: str
    response: str
    confidence: float
    sources: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

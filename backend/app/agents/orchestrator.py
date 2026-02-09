"""
CISO Orchestrator - Central coordination for AI agents.

This module implements the orchestration layer that routes user queries to
appropriate specialized agents based on intent classification and manages
conversation context.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.services.intent_classifier import IntentClassifier, IntentType, Intent
from app.services.conversation_memory import ConversationMemoryService
from app.schemas.orchestrator import OrchestratorResponse, AgentResponse
from app.shared.models.conversation import MessageRole

logger = get_logger(__name__)


# Mapping of intent types to agent names
INTENT_TO_AGENT_MAP = {
    IntentType.RISK_ASSESSMENT: "risk_agent",
    IntentType.INCIDENT_RESPONSE: "incident_agent",
    IntentType.COMPLIANCE_CHECK: "compliance_agent",
    IntentType.THREAT_INTELLIGENCE: "threat_agent",
    IntentType.REPORTING: "reporting_agent",
    IntentType.PROACTIVE_REVIEW: "proactive_agent",
    IntentType.GENERAL_QUERY: None,  # Handled directly
}


# Confidence threshold for clarification
CLARIFICATION_THRESHOLD = 0.7

# Threshold for running multiple agents
MULTI_AGENT_THRESHOLD = 0.7


class CISOOrchestrator:
    """
    Central orchestrator for CISO Digital Assistant.
    
    This class coordinates between intent classification, agent selection,
    execution, and response aggregation. It maintains conversation context
    and handles complex multi-agent scenarios.
    """
    
    def __init__(
        self,
        intent_classifier: IntentClassifier,
        agents: Dict[IntentType, Any],
        conversation_memory: ConversationMemoryService,
        llm_service: Optional[Any] = None
    ):
        """
        Initialize the CISOOrchestrator.
        
        Args:
            intent_classifier: Service for classifying user intents
            agents: Dictionary mapping IntentType to agent instances
            conversation_memory: Service for managing conversation history
            llm_service: Optional LLM service for direct responses
        """
        self.intent_classifier = intent_classifier
        self.agents = agents
        self.conversation_memory = conversation_memory
        self.llm_service = llm_service
        
        logger.info(
            "orchestrator_initialized",
            agents_count=len(agents),
            available_agents=list(agents.keys())
        )
    
    async def process_request(
        self,
        user_query: str,
        session_id: str,
        user_id: str
    ) -> OrchestratorResponse:
        """
        Process a user request through the orchestration pipeline.
        
        This is the main entry point for processing user queries. It:
        1. Retrieves conversation history
        2. Classifies user intent
        3. Determines if clarification is needed
        4. Selects and executes appropriate agent(s)
        5. Aggregates results if multiple agents
        6. Saves conversation to memory
        7. Returns unified response
        
        Args:
            user_query: The user's natural language query
            session_id: Conversation session identifier
            user_id: User identifier
        
        Returns:
            OrchestratorResponse: Complete response with metadata
        
        Raises:
            Exception: If processing fails critically
        """
        logger.info(
            "processing_orchestrator_request",
            session_id=session_id,
            user_id=user_id,
            query_length=len(user_query)
        )
        
        try:
            # Step 1: Retrieve conversation history
            conversation_history = await self.conversation_memory.get_conversation_history(
                session_id=session_id
            )
            
            logger.debug(
                "conversation_history_retrieved",
                session_id=session_id,
                history_length=len(conversation_history)
            )
            
            # Step 2: Save user message
            await self.conversation_memory.save_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=user_query,
                agent_used=None,
                tokens_consumed=0,
                extra_metadata={"user_id": user_id}
            )
            
            # Step 3: Classify intent
            intent = await self.intent_classifier.classify(user_query)
            
            logger.info(
                "intent_classified",
                intent_type=intent.intent_type.value,
                confidence=intent.confidence,
                entities_count=len(intent.entities)
            )
            
            # Step 4: Check if clarification is needed
            if self._should_ask_clarification(intent):
                return await self._handle_clarification_request(
                    intent=intent,
                    session_id=session_id,
                    user_query=user_query
                )
            
            # Step 5: Select agents based on intent
            agents_to_execute = self._select_agents(intent)
            
            # Step 6: Build context for agents
            context = self._build_agent_context(
                user_query=user_query,
                session_id=session_id,
                user_id=user_id,
                conversation_history=conversation_history,
                intent=intent
            )
            
            # Step 7: Handle general queries directly
            if intent.intent_type == IntentType.GENERAL_QUERY:
                return await self._handle_general_query(
                    user_query=user_query,
                    intent=intent,
                    context=context,
                    session_id=session_id
                )
            
            # Step 8: Check if agent is available
            if not agents_to_execute:
                return await self._handle_missing_agent(
                    intent=intent,
                    session_id=session_id,
                    user_query=user_query
                )
            
            # Step 9: Execute agent(s)
            results = await self._execute_agents(
                agents=agents_to_execute,
                user_query=user_query,
                context=context
            )
            
            # Step 10: Aggregate results if multiple agents
            if len(results) > 1:
                aggregated_text = await self._aggregate_results(
                    results=results,
                    user_query=user_query
                )
            else:
                aggregated_text = results[0].response
            
            # Step 11: Format final response
            response = self._format_final_response(
                query=user_query,
                results=results,
                intent=intent,
                aggregated_response=aggregated_text,
                session_id=session_id
            )
            
            # Step 12: Save assistant response
            await self.conversation_memory.save_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=response.response_text,
                agent_used=response.agent_used or ",".join(response.agents_used or []),
                tokens_consumed=0,
                extra_metadata={
                    "intent_type": intent.intent_type.value,
                    "confidence": intent.confidence,
                    "agents_used": response.agents_used,
                    "sources_count": len(response.sources)
                }
            )
            
            logger.info(
                "request_processed_successfully",
                session_id=session_id,
                agents_used=response.agents_used or [response.agent_used],
                confidence=response.confidence
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "orchestrator_processing_error",
                error=str(e),
                error_type=type(e).__name__,
                session_id=session_id
            )
            
            # Create error response
            error_text = "I apologize, but I encountered an error processing your request. Please try again."
            
            # Save error message
            try:
                await self.conversation_memory.save_message(
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    content=error_text,
                    agent_used="orchestrator",
                    tokens_consumed=0,
                    extra_metadata={"error": str(e)}
                )
            except Exception as save_error:
                logger.error(f"Failed to save error message: {save_error}")
            
            return OrchestratorResponse(
                response_text=error_text,
                intent_type="error",
                confidence=0.0,
                session_id=session_id,
                error=str(e)
            )
    
    def _should_ask_clarification(self, intent: Intent) -> bool:
        """
        Determine if clarification is needed based on intent confidence.
        
        Args:
            intent: The classified intent
        
        Returns:
            bool: True if clarification is needed
        """
        return intent.confidence < CLARIFICATION_THRESHOLD
    
    async def _handle_clarification_request(
        self,
        intent: Intent,
        session_id: str,
        user_query: str
    ) -> OrchestratorResponse:
        """
        Handle low-confidence queries by asking for clarification.
        
        Args:
            intent: The ambiguous intent
            session_id: Session identifier
            user_query: Original user query
        
        Returns:
            OrchestratorResponse: Clarification request
        """
        clarification_text = self._build_clarification_question(intent)
        
        logger.info(
            "asking_clarification",
            session_id=session_id,
            confidence=intent.confidence,
            intent_type=intent.intent_type.value
        )
        
        # Save clarification message
        await self.conversation_memory.save_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=clarification_text,
            agent_used="orchestrator",
            tokens_consumed=0,
            extra_metadata={
                "requires_clarification": True,
                "original_intent": intent.intent_type.value,
                "confidence": intent.confidence
            }
        )
        
        return OrchestratorResponse(
            response_text=clarification_text,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence,
            session_id=session_id,
            requires_clarification=True,
            alternative_intents=intent.alternative_intents,
            agent_used="orchestrator"
        )
    
    def _build_clarification_question(self, intent: Intent) -> str:
        """
        Build a clarification question for ambiguous queries.
        
        Args:
            intent: The ambiguous intent
        
        Returns:
            str: Clarification question
        """
        alternatives = []
        
        if intent.alternative_intents:
            for alt in intent.alternative_intents[:3]:  # Top 3 alternatives
                intent_type = alt.get("intent_type", "")
                alternatives.append(self._intent_to_readable(intent_type))
        
        if alternatives:
            alternatives_text = ", ".join(alternatives)
            return (
                f"I'm not entirely sure what you're asking about. "
                f"Could you clarify if you're interested in: {alternatives_text}? "
                f"Or please provide more details about your request."
            )
        else:
            return (
                "I'm not entirely sure what you're asking about. "
                "Could you please provide more details or rephrase your question?"
            )
    
    def _intent_to_readable(self, intent_type: str) -> str:
        """Convert intent type to readable text."""
        readable_map = {
            "risk_assessment": "risk assessment",
            "incident_response": "incident response",
            "compliance_check": "compliance checking",
            "threat_intelligence": "threat intelligence",
            "reporting": "generating reports",
            "proactive_review": "proactive security review",
            "general_query": "general security information"
        }
        return readable_map.get(intent_type, intent_type.replace("_", " "))
    
    def _select_agents(self, intent: Intent) -> List[Any]:
        """
        Select agents to execute based on intent.
        
        Args:
            intent: The classified intent
        
        Returns:
            List of agents to execute
        """
        agents_to_execute = []
        
        # Primary agent
        primary_agent = self.agents.get(intent.intent_type)
        if primary_agent:
            agents_to_execute.append(primary_agent)
        
        # Check for additional agents from alternative intents
        if intent.alternative_intents:
            for alt in intent.alternative_intents:
                alt_confidence = alt.get("confidence", 0.0)
                if alt_confidence >= MULTI_AGENT_THRESHOLD:
                    alt_intent_type = alt.get("intent_type")
                    if alt_intent_type:
                        try:
                            alt_type = IntentType(alt_intent_type)
                            alt_agent = self.agents.get(alt_type)
                            if alt_agent and alt_agent not in agents_to_execute:
                                agents_to_execute.append(alt_agent)
                        except ValueError:
                            logger.warning(f"Invalid alternative intent type: {alt_intent_type}")
        
        logger.debug(
            "agents_selected",
            primary_intent=intent.intent_type.value,
            agents_count=len(agents_to_execute)
        )
        
        return agents_to_execute
    
    def _build_agent_context(
        self,
        user_query: str,
        session_id: str,
        user_id: str,
        conversation_history: List[Any],
        intent: Intent
    ) -> Dict[str, Any]:
        """
        Build context dictionary for agent execution.
        
        Args:
            user_query: User's query
            session_id: Session identifier
            user_id: User identifier
            conversation_history: Previous messages
            intent: Classified intent
        
        Returns:
            Context dictionary
        """
        return {
            "session_id": session_id,
            "user_id": user_id,
            "conversation_history": conversation_history,
            "intent": intent,
            "entities": intent.entities,
            "user_query": user_query,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_general_query(
        self,
        user_query: str,
        intent: Intent,
        context: Dict[str, Any],
        session_id: str
    ) -> OrchestratorResponse:
        """
        Handle general queries directly without specialized agents.
        
        Args:
            user_query: User's query
            intent: Classified intent
            context: Request context
            session_id: Session identifier
        
        Returns:
            OrchestratorResponse: Direct response
        """
        logger.info("handling_general_query", query=user_query[:50])
        
        # For now, return a simple response
        # In production, this would call LLM directly
        response_text = (
            f"This is a general security question. "
            f"I can provide information about: {user_query}. "
            f"However, for more specific assistance, please ask about "
            f"risk assessment, incident response, or compliance checks."
        )
        
        # Save response
        await self.conversation_memory.save_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            agent_used="DirectResponse",
            tokens_consumed=0,
            extra_metadata={"intent_type": intent.intent_type.value}
        )
        
        return OrchestratorResponse(
            response_text=response_text,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence,
            session_id=session_id,
            agent_used="DirectResponse"
        )
    
    async def _handle_missing_agent(
        self,
        intent: Intent,
        session_id: str,
        user_query: str
    ) -> OrchestratorResponse:
        """
        Handle case when no agent is available for the intent.
        
        Args:
            intent: The intent without a registered agent
            session_id: Session identifier
            user_query: User's original query
        
        Returns:
            OrchestratorResponse: Error response
        """
        logger.warning(
            "no_agent_available",
            intent_type=intent.intent_type.value
        )
        
        error_text = (
            f"I understand you're asking about {self._intent_to_readable(intent.intent_type.value)}, "
            f"but that capability is not available yet. "
            f"Please try asking about risk assessment, incident response, or compliance checking."
        )
        
        # Save error response
        await self.conversation_memory.save_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=error_text,
            agent_used="DirectResponse",
            tokens_consumed=0,
            extra_metadata={
                "intent_type": intent.intent_type.value,
                "agent_not_available": True
            }
        )
        
        return OrchestratorResponse(
            response_text=error_text,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence,
            session_id=session_id,
            agent_used="DirectResponse",
            error="Agent not available"
        )
    
    async def _execute_agents(
        self,
        agents: List[Any],
        user_query: str,
        context: Dict[str, Any]
    ) -> List[AgentResponse]:
        """
        Execute selected agents with the given context.
        
        Args:
            agents: List of agents to execute
            user_query: User's query
            context: Execution context
        
        Returns:
            List of agent responses
        """
        logger.info(
            "executing_agents",
            agents_count=len(agents)
        )
        
        # Execute agents in parallel
        tasks = []
        for agent in agents:
            task = self._execute_single_agent(agent, user_query, context)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = getattr(agents[i], "name", f"agent_{i}")
                logger.error(
                    "agent_execution_failed",
                    agent_name=agent_name,
                    error=str(result)
                )
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _execute_single_agent(
        self,
        agent: Any,
        user_query: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute a single agent.
        
        Args:
            agent: The agent to execute
            user_query: User's query
            context: Execution context
        
        Returns:
            AgentResponse: Agent's response
        """
        agent_name = getattr(agent, "name", agent.__class__.__name__)
        
        logger.debug(
            "executing_single_agent",
            agent_name=agent_name
        )
        
        try:
            # Call agent's process method
            result = await agent.process(
                query=user_query,
                context=context,
                entities=context.get("entities", []),
                conversation_history=context.get("conversation_history", [])
            )
            
            # Convert agent result to AgentResponse
            if isinstance(result, dict):
                response_text = result.get("response", str(result))
                sources = result.get("sources", [])
                confidence = result.get("confidence", 0.9)
                metadata = result
            else:
                response_text = str(result)
                sources = []
                confidence = 0.9
                metadata = {}
            
            return AgentResponse(
                agent_name=agent_name,
                response=response_text,
                confidence=confidence,
                sources=sources,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(
                "single_agent_execution_error",
                agent_name=agent_name,
                error=str(e)
            )
            raise
    
    async def _aggregate_results(
        self,
        results: List[AgentResponse],
        user_query: str
    ) -> str:
        """
        Aggregate results from multiple agents.
        
        Args:
            results: List of agent responses
            user_query: Original user query
        
        Returns:
            str: Aggregated response text
        """
        logger.info(
            "aggregating_results",
            results_count=len(results)
        )
        
        # Simple aggregation: combine all responses with headers
        aggregated = f"Based on your query: '{user_query}'\n\n"
        
        for i, result in enumerate(results, 1):
            aggregated += f"### {result.agent_name}\n"
            aggregated += f"{result.response}\n\n"
            
            if result.sources:
                aggregated += f"**Sources:** {', '.join(result.sources[:3])}\n\n"
        
        aggregated += "---\n\n"
        aggregated += "**Summary:** "
        
        # Extract key points
        if len(results) == 1:
            aggregated += "Please review the analysis above."
        else:
            aggregated += f"I've analyzed your query from {len(results)} perspectives. "
            aggregated += "Please review the detailed findings above."
        
        return aggregated
    
    def _format_final_response(
        self,
        query: str,
        results: List[AgentResponse],
        intent: Intent,
        aggregated_response: str,
        session_id: str
    ) -> OrchestratorResponse:
        """
        Format the final orchestrator response.
        
        Args:
            query: Original user query
            results: Agent responses
            intent: Classified intent
            aggregated_response: Aggregated response text
            session_id: Session identifier
        
        Returns:
            OrchestratorResponse: Final formatted response
        """
        # Collect all sources
        all_sources = []
        for result in results:
            all_sources.extend(result.sources)
        
        # Get agent names
        agent_names = [result.agent_name for result in results]
        
        # Build agent_results dict
        agent_results_dict = {
            result.agent_name: result.metadata or {"response": result.response}
            for result in results
        }
        
        return OrchestratorResponse(
            response_text=aggregated_response,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence,
            session_id=session_id,
            agent_used=agent_names[0] if len(agent_names) == 1 else None,
            agents_used=agent_names if len(agent_names) > 1 else None,
            agent_results=agent_results_dict,
            sources=list(set(all_sources)),  # Deduplicate
            requires_clarification=False
        )

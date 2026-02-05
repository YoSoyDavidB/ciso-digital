"""
Base Agent Class - Abstract base for all AI agents in CISO Digital.

Uses GitHub Copilot SDK for AI capabilities with tool calling support.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.copilot_service import CopilotService
from app.services.rag_service import RAGService


logger = logging.getLogger(__name__)


@dataclass
class Task:
    """
    Task input for agent execution.

    Attributes:
        query: Main query or request for the agent
        context: Additional context information
        parameters: Execution parameters
    """

    query: str
    context: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """
    Response from agent execution.

    Attributes:
        response: Main response text from the agent
        confidence: Confidence score (0.0 to 1.0)
        sources: List of source references used
        actions_taken: List of actions performed
    """

    response: str
    confidence: float
    sources: list[str] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Provides common functionality for:
    - Session management with GitHub Copilot SDK
    - RAG integration for context gathering
    - Logging and observability
    - Fallback to Azure OpenAI

    Subclasses must implement:
    - get_system_prompt(): Returns agent-specific system prompt
    - get_tools(): Returns agent-specific tools
    - execute(): Main agent logic

    Example:
        >>> class MyAgent(BaseAgent):
        ...     async def get_system_prompt(self) -> str:
        ...         return "You are a security analyst"
        ...
        ...     def get_tools(self) -> list:
        ...         @define_tool
        ...         async def analyze_risk(risk_id: str) -> dict:
        ...             return {"risk_id": risk_id, "severity": "high"}
        ...         return [analyze_risk]
        ...
        ...     async def execute(self, task: Task) -> AgentResponse:
        ...         response = await self.chat(task.query)
        ...         return AgentResponse(response, 0.9, [], [])
    """

    def __init__(
        self, copilot_service: CopilotService, rag_service: RAGService, db_session: AsyncSession
    ):
        """
        Initialize BaseAgent.

        Args:
            copilot_service: GitHub Copilot SDK service instance
            rag_service: RAG service for context retrieval
            db_session: Database session for data access
        """
        self.copilot_service = copilot_service
        self.rag_service = rag_service
        self.db_session = db_session
        self.name = self.__class__.__name__
        self.session: Any | None = None
        self.using_azure = False

        logger.info(f"🤖 Initialized {self.name}")

    @abstractmethod
    async def get_system_prompt(self) -> str:
        """
        Get agent-specific system prompt.

        Returns:
            System prompt string defining the agent's role and behavior

        Example:
            >>> async def get_system_prompt(self) -> str:
            ...     return '''You are a security risk assessment expert.
            ...     Analyze risks and provide actionable recommendations.'''
        """
        pass

    @abstractmethod
    def get_tools(self) -> list:
        """
        Get agent-specific tools.

        Returns:
            List of tool functions decorated with @define_tool

        Example:
            >>> def get_tools(self) -> list:
            ...     @define_tool
            ...     async def search_cve(cve_id: str) -> dict:
            ...         '''Search for CVE information.'''
            ...         return {"cve_id": cve_id, "severity": "critical"}
            ...     return [search_cve]
        """
        pass

    @abstractmethod
    async def execute(self, task: Task) -> AgentResponse:
        """
        Execute agent's main logic.

        Args:
            task: Task to execute

        Returns:
            AgentResponse with results

        Example:
            >>> async def execute(self, task: Task) -> AgentResponse:
            ...     # Gather context
            ...     context = await self.gather_context(task.query, "security_knowledge")
            ...
            ...     # Process with AI
            ...     response = await self.chat(f"{task.query}\\nContext: {context}")
            ...
            ...     # Log action
            ...     await self.log_action("task_completed", {"query": task.query})
            ...
            ...     return AgentResponse(response, 0.95, sources=[], actions_taken=["chat"])
        """
        pass

    async def initialize_session(self) -> None:
        """
        Initialize Copilot SDK session with system prompt and tools.

        Creates a new session with:
        - Agent-specific system prompt
        - Agent-specific tools
        - Default model from settings

        Example:
            >>> await agent.initialize_session()
            >>> # Session is now ready for chat()
        """
        await self.get_system_prompt()
        tools = self.get_tools()

        logger.info(f"🔧 Initializing session for {self.name} with {len(tools)} tools")

        self.session = await self.copilot_service.create_session()

        logger.info(f"✅ Session initialized for {self.name}")

    async def chat(self, message: str) -> str:
        """
        Send message to agent's Copilot session.

        Automatically initializes session if not already created.

        Args:
            message: Message to send to the AI

        Returns:
            AI response as string

        Example:
            >>> response = await agent.chat("What are the top security risks?")
            >>> print(response)
            "Top risks include SQL injection, XSS, and CSRF..."
        """
        if self.session is None:
            await self.initialize_session()

        logger.debug(f"💬 {self.name} chat: {message[:100]}...")

        # Use copilot_service.chat() to handle both CopilotSession and Azure dict
        response_dict = await self.copilot_service.chat(self.session, message)
        response_text = response_dict["text"]

        logger.debug(f"🤖 {self.name} response: {response_text[:100]}...")

        return response_text

    async def gather_context(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Gather relevant context using RAG service.

        Args:
            query: Search query
            limit: Maximum number of results (default: 5)

        Returns:
            List of relevant documents with text and scores

        Example:
            >>> docs = await agent.gather_context(
            ...     "ISO 27001 controls",
            ...     limit=10
            ... )
            >>> for doc in docs:
            ...     print(f"{doc['score']:.2f}: {doc['text'][:50]}")
        """
        logger.info(f"🔍 {self.name} gathering context: {query}")

        documents = await self.rag_service.search(query=query, limit=limit)

        logger.info(f"📚 Found {len(documents)} relevant documents")

        return documents

    async def log_action(self, action: str, metadata: dict[str, Any]) -> None:
        """
        Log agent action with structured metadata.

        Args:
            action: Action name/type
            metadata: Additional context and data

        Example:
            >>> await agent.log_action(
            ...     "risk_assessed",
            ...     {"risk_id": "R001", "severity": "high", "confidence": 0.92}
            ... )
        """
        logger.info(
            f"🎯 {self.name} action: {action}",
            extra={"agent": self.name, "action": action, "metadata": metadata},
        )

    async def fallback_to_azure(self) -> None:
        """
        Fallback to Azure OpenAI if Copilot SDK fails.

        Creates new session using Azure OpenAI instead of GitHub Copilot.
        Useful for reliability when Copilot is unavailable.

        Example:
            >>> try:
            ...     await agent.initialize_session()
            ... except Exception:
            ...     logger.warning("Copilot unavailable, falling back to Azure")
            ...     await agent.fallback_to_azure()
        """
        logger.warning(f"⚠️ {self.name} falling back to Azure OpenAI")

        if not all(
            [
                settings.AZURE_OPENAI_KEY,
                settings.AZURE_OPENAI_ENDPOINT,
                settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            ]
        ):
            raise RuntimeError(
                "Azure OpenAI configuration missing. "
                "Cannot fallback without AZURE_OPENAI_KEY, ENDPOINT, and CHAT_DEPLOYMENT"
            )

        self.using_azure = True

        # Re-initialize session with Azure (Copilot SDK will handle internally)
        await self.initialize_session()

        logger.info(f"✅ {self.name} now using Azure OpenAI")

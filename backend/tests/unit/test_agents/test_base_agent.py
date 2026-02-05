"""
🔴 RED: Tests para BaseAgent - TDD Phase

Estos tests DEBEN FALLAR porque BaseAgent no existe aún.

Tests de:
- Inicialización de BaseAgent
- Métodos abstractos (get_system_prompt, get_tools, execute)
- Métodos concretos (initialize_session, chat, gather_context, log_action)
- Fallback a Azure OpenAI
- Tool calling integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# 🔴 RED: Este import DEBE fallar porque BaseAgent no existe
from app.agents.base_agent import BaseAgent, Task, AgentResponse
from app.services.copilot_service import CopilotService
from app.services.rag_service import RAGService


class TestBaseAgentInitialization:
    """Tests de inicialización de BaseAgent."""
    
    def test_base_agent_is_abstract(self):
        """
        🔴 RED: BaseAgent debe ser abstracta y no instanciable directamente.
        
        Given: BaseAgent es una clase abstracta
        When: Se intenta instanciar directamente
        Then: Lanza TypeError
        """
        mock_copilot = MagicMock(spec=CopilotService)
        mock_rag = MagicMock(spec=RAGService)
        mock_db = MagicMock(spec=AsyncSession)
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseAgent(
                copilot_service=mock_copilot,
                rag_service=mock_rag,
                db_session=mock_db
            )
    
    def test_concrete_agent_requires_abstract_methods(self):
        """
        🔴 RED: Agente concreto debe implementar métodos abstractos.
        
        Given: Clase que hereda de BaseAgent sin implementar métodos abstractos
        When: Se intenta instanciar
        Then: Lanza TypeError
        """
        class IncompleteAgent(BaseAgent):
            pass  # No implementa métodos abstractos
        
        mock_copilot = MagicMock(spec=CopilotService)
        mock_rag = MagicMock(spec=RAGService)
        mock_db = MagicMock(spec=AsyncSession)
        
        with pytest.raises(TypeError):
            IncompleteAgent(
                copilot_service=mock_copilot,
                rag_service=mock_rag,
                db_session=mock_db
            )
    
    def test_concrete_agent_can_be_instantiated(self):
        """
        🔴 RED: Agente concreto completo puede instanciarse.
        
        Given: Clase que implementa todos los métodos abstractos
        When: Se instancia
        Then: Se crea correctamente
        """
        class CompleteAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test prompt"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse(
                    response="Test response",
                    confidence=0.95,
                    sources=[],
                    actions_taken=[]
                )
        
        mock_copilot = MagicMock(spec=CopilotService)
        mock_rag = MagicMock(spec=RAGService)
        mock_db = MagicMock(spec=AsyncSession)
        
        agent = CompleteAgent(
            copilot_service=mock_copilot,
            rag_service=mock_rag,
            db_session=mock_db
        )
        
        assert agent is not None
        assert agent.name == "CompleteAgent"
        assert agent.copilot_service == mock_copilot
        assert agent.rag_service == mock_rag
        assert agent.db_session == mock_db
        assert agent.session is None


class TestBaseAgentSessionManagement:
    """Tests de gestión de sesiones de Copilot."""
    
    @pytest.mark.asyncio
    async def test_initialize_session_creates_copilot_session(self):
        """
        🔴 RED: initialize_session crea sesión con Copilot SDK.
        
        Given: BaseAgent con Copilot configurado
        When: Se llama initialize_session()
        Then: Crea sesión con system prompt y tools
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "You are a test agent"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_copilot = AsyncMock(spec=CopilotService)
        mock_session = AsyncMock()
        mock_copilot.create_session.return_value = mock_session
        
        agent = TestAgent(
            copilot_service=mock_copilot,
            rag_service=MagicMock(),
            db_session=MagicMock()
        )
        
        await agent.initialize_session()
        
        assert agent.session == mock_session
        mock_copilot.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chat_initializes_session_if_needed(self):
        """
        🔴 RED: chat() inicializa sesión automáticamente si no existe.
        
        Given: BaseAgent sin sesión activa
        When: Se llama chat()
        Then: Inicializa sesión y envía mensaje
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_copilot = AsyncMock(spec=CopilotService)
        mock_session = AsyncMock()
        # Mock create_session to return a mock session
        mock_copilot.create_session.return_value = mock_session
        # Mock copilot_service.chat() to return dict with "text" key
        mock_copilot.chat.return_value = {"text": "Response from AI", "model": "test", "provider": "test", "tokens": 0, "tool_calls": []}
        
        agent = TestAgent(
            copilot_service=mock_copilot,
            rag_service=MagicMock(),
            db_session=MagicMock()
        )
        
        response = await agent.chat("Hello")
        
        assert agent.session is not None
        assert response == "Response from AI"
        mock_copilot.create_session.assert_called_once()
        # Verify copilot_service.chat was called with session and message
        mock_copilot.chat.assert_called_once_with(mock_session, "Hello")
    
    @pytest.mark.asyncio
    async def test_chat_reuses_existing_session(self):
        """
        🔴 RED: chat() reutiliza sesión existente.
        
        Given: BaseAgent con sesión activa
        When: Se llama chat() múltiples veces
        Then: Reutiliza la misma sesión
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_copilot = AsyncMock(spec=CopilotService)
        mock_session = AsyncMock()
        mock_copilot.create_session.return_value = mock_session
        # Mock copilot_service.chat()
        mock_copilot.chat.return_value = {"text": "Response", "model": "test", "provider": "test", "tokens": 0, "tool_calls": []}
        
        agent = TestAgent(
            copilot_service=mock_copilot,
            rag_service=MagicMock(),
            db_session=MagicMock()
        )
        
        await agent.initialize_session()
        first_session = agent.session
        
        await agent.chat("Message 1")
        await agent.chat("Message 2")
        
        assert agent.session is first_session
        assert mock_copilot.create_session.call_count == 1
        # Verify copilot_service.chat was called twice
        assert mock_copilot.chat.call_count == 2


class TestBaseAgentRAGIntegration:
    """Tests de integración con RAG Service."""
    
    @pytest.mark.asyncio
    async def test_gather_context_uses_rag_service(self):
        """
        🔴 RED: gather_context() usa RAG para buscar documentos.
        
        Given: Query y collection name
        When: Se llama gather_context()
        Then: Busca en RAG y retorna documentos relevantes
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = [
            {"text": "Doc 1", "score": 0.95},
            {"text": "Doc 2", "score": 0.87}
        ]
        
        agent = TestAgent(
            copilot_service=MagicMock(),
            rag_service=mock_rag,
            db_session=MagicMock()
        )
        
        docs = await agent.gather_context(query="ISO 27001 controls")
        
        assert len(docs) == 2
        mock_rag.search.assert_called_once_with(query="ISO 27001 controls", limit=5)
    
    @pytest.mark.asyncio
    async def test_gather_context_with_custom_limit(self):
        """
        🔴 RED: gather_context() permite especificar límite de resultados.
        
        Given: Query con limit customizado
        When: Se llama gather_context(limit=10)
        Then: Busca con el límite especificado
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_rag = AsyncMock(spec=RAGService)
        mock_rag.search.return_value = []
        
        agent = TestAgent(
            copilot_service=MagicMock(),
            rag_service=mock_rag,
            db_session=MagicMock()
        )
        
        await agent.gather_context("query", limit=10)
        
        mock_rag.search.assert_called_once_with(query="query", limit=10)


class TestBaseAgentFallback:
    """Tests de fallback a Azure OpenAI."""
    
    @pytest.mark.asyncio
    async def test_fallback_to_azure_creates_azure_session(self):
        """
        🔴 RED: fallback_to_azure() crea sesión con Azure OpenAI.
        
        Given: BaseAgent con configuración de Azure
        When: Se llama fallback_to_azure()
        Then: Crea sesión con Azure OpenAI
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        mock_copilot = AsyncMock(spec=CopilotService)
        mock_session = AsyncMock()
        mock_copilot.chat_with_tools.return_value = {"content": "Azure response"}
        
        agent = TestAgent(
            copilot_service=mock_copilot,
            rag_service=MagicMock(),
            db_session=MagicMock()
        )
        
        await agent.fallback_to_azure()
        
        # Verifica que se intentó usar Azure
        assert agent.using_azure is True


class TestBaseAgentLogging:
    """Tests de logging y observabilidad."""
    
    @pytest.mark.asyncio
    async def test_log_action_records_agent_actions(self):
        """
        🔴 RED: log_action() registra acciones del agente.
        
        Given: Acción y metadata
        When: Se llama log_action()
        Then: Registra en logs con formato estructurado
        """
        class TestAgent(BaseAgent):
            async def get_system_prompt(self) -> str:
                return "Test"
            
            def get_tools(self) -> list:
                return []
            
            async def execute(self, task: Task) -> AgentResponse:
                return AgentResponse("test", 0.9, [], [])
        
        agent = TestAgent(
            copilot_service=MagicMock(),
            rag_service=MagicMock(),
            db_session=MagicMock()
        )
        
        with patch('app.agents.base_agent.logger') as mock_logger:
            await agent.log_action(
                action="risk_assessment",
                metadata={"risk_id": "R001", "severity": "high"}
            )
            
            mock_logger.info.assert_called_once()
            # Verificar que se incluye el nombre del agente y metadata
            call_args = mock_logger.info.call_args[0][0]
            assert "TestAgent" in call_args
            assert "risk_assessment" in call_args


class TestTaskAndResponse:
    """Tests de tipos Task y AgentResponse."""
    
    def test_task_can_be_created(self):
        """
        🔴 RED: Task puede crearse con query y parámetros.
        
        Given: Datos de tarea
        When: Se crea Task
        Then: Se crea correctamente
        """
        task = Task(
            query="Assess risk for SQL injection",
            context={"asset": "web-app-prod"},
            parameters={"severity_threshold": "high"}
        )
        
        assert task.query == "Assess risk for SQL injection"
        assert task.context["asset"] == "web-app-prod"
        assert task.parameters["severity_threshold"] == "high"
    
    def test_agent_response_can_be_created(self):
        """
        🔴 RED: AgentResponse puede crearse con respuesta y metadata.
        
        Given: Datos de respuesta
        When: Se crea AgentResponse
        Then: Se crea correctamente
        """
        response = AgentResponse(
            response="Risk level: HIGH. Immediate action required.",
            confidence=0.92,
            sources=["ISO 27001:A.12.6.1", "NIST 800-53:SI-10"],
            actions_taken=["created_ticket", "notified_team"]
        )
        
        assert response.response.startswith("Risk level: HIGH")
        assert response.confidence == 0.92
        assert len(response.sources) == 2
        assert "created_ticket" in response.actions_taken
    
    def test_agent_response_validates_confidence(self):
        """
        🔴 RED: AgentResponse valida que confidence esté entre 0 y 1.
        
        Given: Confidence inválido
        When: Se crea AgentResponse
        Then: Lanza ValueError
        """
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            AgentResponse(
                response="Test",
                confidence=1.5,  # Inválido
                sources=[],
                actions_taken=[]
            )

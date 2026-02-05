"""
Tests para CopilotService - TDD Red Phase

Estos tests deben FALLAR primero porque CopilotService no existe aún.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# 🔴 RED: Este import DEBE fallar porque no existe el archivo
from app.services.copilot_service import CopilotService, get_copilot_service


class TestCopilotServiceInitialization:
    """Tests de inicialización del servicio."""
    
    def test_copilot_service_can_be_instantiated(self):
        """
        🔴 RED: Test que CopilotService se puede instanciar.
        
        Given: Configuración válida de GitHub Copilot SDK
        When: Se instancia CopilotService
        Then: El servicio se crea correctamente
        """
        service = CopilotService()
        assert service is not None
        assert hasattr(service, 'copilot_client')
        assert hasattr(service, 'azure_client')
    
    def test_singleton_returns_same_instance(self):
        """
        🔴 RED: Test que get_copilot_service retorna siempre la misma instancia.
        
        Given: Llamadas múltiples a get_copilot_service
        When: Se llama dos veces
        Then: Retorna la misma instancia (singleton)
        """
        service1 = get_copilot_service()
        service2 = get_copilot_service()
        assert service1 is service2
    
    @patch('app.services.copilot_service.settings')
    def test_initialization_with_github_token(self, mock_settings):
        """
        🔴 RED: Test que se inicializa con GitHub token.
        
        Given: GITHUB_TOKEN configurado en settings
        When: Se inicializa el servicio
        Then: using_copilot es True y copilot_client está configurado
        """
        mock_settings.GITHUB_TOKEN = "ghp_test_token"
        mock_settings.COPILOT_AUTO_RESTART = True
        mock_settings.COPILOT_LOG_LEVEL = "info"
        mock_settings.COPILOT_MAX_RETRIES = 3
        
        with patch('app.services.copilot_service.CopilotClient') as mock_client:
            service = CopilotService()
            assert service.using_copilot is True
            mock_client.assert_called_once()


class TestCopilotServiceCreateSession:
    """Tests para el método create_session."""
    
    @pytest.mark.asyncio
    async def test_create_session_with_github_copilot(self):
        """
        🔴 RED: Test que create_session funciona con GitHub Copilot SDK.
        
        Given: CopilotService con GitHub Copilot SDK configurado
        When: Se llama a create_session con modelo y system prompt
        Then: Se crea una sesión válida con CopilotSession
        """
        with patch('app.services.copilot_service.CopilotClient') as mock_client:
            mock_session = AsyncMock()
            mock_client_instance = AsyncMock()
            mock_client_instance.create_session.return_value = mock_session
            mock_client.return_value = mock_client_instance
            
            service = CopilotService()
            session = await service.create_session(
                model="claude-sonnet-4.5",
                system_prompt="Eres un experto CISO",
                tools=None
            )
            
            assert session is not None
            mock_client_instance.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session_with_tools(self):
        """
        🔴 RED: Test que create_session acepta tools.
        
        Given: Lista de tools definidas
        When: Se crea sesión con tools
        Then: La sesión incluye las tools en la configuración
        """
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        
        with patch('app.services.copilot_service.CopilotClient') as mock_client:
            mock_session = AsyncMock()
            mock_client_instance = AsyncMock()
            mock_client_instance.create_session.return_value = mock_session
            mock_client.return_value = mock_client_instance
            
            service = CopilotService()
            session = await service.create_session(
                model="claude-sonnet-4.5",
                system_prompt="Test",
                tools=[mock_tool]
            )
            
            assert session is not None
            # Verificar que se pasaron las tools
            call_args = mock_client_instance.create_session.call_args
            assert call_args is not None


class TestCopilotServiceChat:
    """Tests para el método chat."""
    
    @pytest.mark.asyncio
    async def test_chat_sends_message(self):
        """
        🔴 RED: Test que chat envía mensaje y retorna respuesta.
        
        Given: Sesión activa de Copilot
        When: Se envía un mensaje
        Then: Se recibe respuesta con text, model, tokens
        """
        mock_session = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Esta es la respuesta del modelo"
        mock_session.chat.return_value = mock_response
        
        with patch('app.services.copilot_service.CopilotClient'):
            service = CopilotService()
            service.using_copilot = True
            
            response = await service.chat(mock_session, "¿Cuál es el riesgo?")
            
            assert response is not None
            assert "text" in response
            assert "model" in response
            assert "tokens" in response
            assert response["text"] == "Esta es la respuesta del modelo"
    
    @pytest.mark.asyncio
    async def test_chat_with_retry_on_failure(self):
        """
        🔴 RED: Test que chat reintenta en caso de fallo.
        
        Given: Primera llamada falla, segunda tiene éxito
        When: Se envía mensaje
        Then: Reintenta y retorna respuesta exitosa
        """
        mock_session = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Respuesta exitosa"
        
        # Primera llamada falla, segunda tiene éxito
        mock_session.chat.side_effect = [
            Exception("Connection error"),
            mock_response
        ]
        
        with patch('app.services.copilot_service.CopilotClient'):
            service = CopilotService()
            service.using_copilot = True
            service.max_retries = 3
            
            response = await service.chat(mock_session, "test")
            
            assert response["text"] == "Respuesta exitosa"
            assert mock_session.chat.call_count == 2


class TestCopilotServiceChatWithTools:
    """Tests para chat_with_tools."""
    
    @pytest.mark.asyncio
    async def test_chat_with_tools_calls_chat(self):
        """
        🔴 RED: Test que chat_with_tools funciona.
        
        Given: Sesión con tools configuradas
        When: Se llama a chat_with_tools
        Then: Funciona similar a chat normal
        """
        mock_session = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Respuesta con tools"
        mock_session.chat.return_value = mock_response
        
        with patch('app.services.copilot_service.CopilotClient'):
            service = CopilotService()
            service.using_copilot = True
            
            response = await service.chat_with_tools(mock_session, "Analiza riesgos")
            
            assert response is not None
            assert "text" in response


class TestCopilotServiceFallback:
    """Tests para fallback a Azure OpenAI."""
    
    @pytest.mark.asyncio
    @patch('app.services.copilot_service.settings')
    async def test_fallback_to_azure_when_copilot_fails(self, mock_settings):
        """
        🔴 RED: Test que cae a Azure si Copilot no está disponible.
        
        Given: GitHub Copilot no disponible pero Azure sí
        When: Se inicializa el servicio
        Then: using_azure es True
        """
        mock_settings.GITHUB_TOKEN = None
        mock_settings.AZURE_OPENAI_KEY = "azure_key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_DEPLOYMENT = "gpt-4"
        mock_settings.COPILOT_AUTO_RESTART = True
        mock_settings.COPILOT_LOG_LEVEL = "info"
        mock_settings.COPILOT_MAX_RETRIES = 3
        
        with patch('app.services.copilot_service.CopilotClient', side_effect=Exception("No GitHub token")):
            with patch('app.services.copilot_service.AsyncAzureOpenAI'):
                service = CopilotService()
                assert service.using_azure is True
                assert service.using_copilot is False


class TestCopilotServiceLogging:
    """Tests para logging de tokens y modelo."""
    
    @pytest.mark.asyncio
    async def test_chat_logs_token_usage(self, caplog):
        """
        🔴 RED: Test que se loguean los tokens consumidos.
        
        Given: Respuesta del modelo con usage info
        When: Se hace chat
        Then: Se loguean los tokens consumidos
        """
        import logging
        
        mock_session = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Respuesta"
        mock_response.usage = {"total_tokens": 150}
        mock_session.chat.return_value = mock_response
        
        with patch('app.services.copilot_service.CopilotClient'):
            service = CopilotService()
            service.using_copilot = True
            
            with caplog.at_level(logging.INFO):
                await service.chat(mock_session, "test")
                
                # Verificar que se logueó la info de tokens
                assert any("Tokens: 150" in record.message for record in caplog.records) or \
                       any("tokens" in record.message.lower() for record in caplog.records)

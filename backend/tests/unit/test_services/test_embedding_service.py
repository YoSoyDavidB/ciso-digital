"""
Tests para EmbeddingService - TDD Red Phase

Estos tests deben FALLAR primero porque EmbeddingService no existe aún.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# 🔴 RED: Este import DEBE fallar porque no existe el archivo
from app.services.embedding_service import EmbeddingService, get_embedding_service


class TestEmbeddingServiceInitialization:
    """Tests de inicialización del servicio."""
    
    @patch('app.services.embedding_service.AsyncAzureOpenAI')
    @patch('app.services.embedding_service.AsyncOpenAI')
    @patch('app.services.embedding_service.settings')
    def test_embedding_service_can_be_instantiated(self, mock_settings, mock_openai_class, mock_azure_class):
        """
        🔴 RED: Test que EmbeddingService se puede instanciar.
        
        Given: Configuración válida
        When: Se instancia EmbeddingService
        Then: El servicio se crea correctamente
        """
        mock_settings.AZURE_OPENAI_KEY = "test-azure-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_client = AsyncMock()
        mock_azure_class.return_value = mock_client
        
        service = EmbeddingService()
        assert service is not None
        assert hasattr(service, 'embed')
        assert hasattr(service, 'embed_batch')
    
    @patch('app.services.embedding_service.AsyncAzureOpenAI')
    @patch('app.services.embedding_service.AsyncOpenAI')
    @patch('app.services.embedding_service.settings')
    def test_singleton_returns_same_instance(self, mock_settings, mock_openai_class, mock_azure_class):
        """
        🔴 RED: Test que get_embedding_service retorna la misma instancia.
        
        Given: Llamadas múltiples a get_embedding_service
        When: Se llama dos veces
        Then: Retorna la misma instancia (singleton)
        """
        mock_settings.AZURE_OPENAI_KEY = "test-azure-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_client = AsyncMock()
        mock_azure_class.return_value = mock_client
        
        # Clear any existing cached service
        import app.services.embedding_service as es_module
        es_module._embedding_service = None
        get_embedding_service.cache_clear()
        
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        assert service1 is service2
    
    @patch('app.services.embedding_service.settings')
    def test_initialization_with_openai(self, mock_settings):
        """
        🔴 RED: Test que se inicializa con OpenAI si hay API key.
        
        Given: OPENAI_API_KEY configurado
        When: Se inicializa el servicio
        Then: using_openai es True
        """
        mock_settings.OPENAI_API_KEY = "sk-test-key"
        
        with patch('app.services.embedding_service.AsyncOpenAI'):
            service = EmbeddingService()
            assert service.using_openai is True
    
    @patch('app.services.embedding_service.settings')
    def test_initialization_fallback_to_local(self, mock_settings):
        """
        🔴 RED: Test que cae a local si no hay OpenAI key.
        
        Given: Sin OPENAI_API_KEY
        When: Se inicializa el servicio
        Then: using_local es True
        """
        mock_settings.OPENAI_API_KEY = None
        
        with patch('app.services.embedding_service.SentenceTransformer'):
            service = EmbeddingService()
            assert service.using_local is True


class TestEmbeddingServiceEmbed:
    """Tests para el método embed."""
    
    @pytest.mark.asyncio
    async def test_embed_single_text_with_openai(self):
        """
        🔴 RED: Test que embed genera embedding con Azure OpenAI.
        
        Given: Texto simple y Azure OpenAI configurado
        When: Se llama a embed(text)
        Then: Retorna vector de 1536 dimensiones
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_azure.return_value = mock_client
            
            service = EmbeddingService()
            service.using_azure = True
            service.deployment_name = "test-deployment"
            
            embedding = await service.embed("Test text")
            
            assert len(embedding) == 1536
            assert isinstance(embedding, list)
            assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_embed_returns_cached_result(self):
        """
        🔴 RED: Test que embed usa cache para textos repetidos.
        
        Given: Mismo texto embebido dos veces
        When: Se llama a embed dos veces con mismo texto
        Then: Segunda llamada usa cache (no llama a API)
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_azure.return_value = mock_client
            
            service = EmbeddingService()
            service.using_azure = True
            service.deployment_name = "test-deployment"
            
            text = "Same text"
            embedding1 = await service.embed(text)
            embedding2 = await service.embed(text)
            
            assert embedding1 == embedding2
            # Solo una llamada a la API (segunda usa cache)
            assert mock_client.embeddings.create.call_count == 1
    
    @pytest.mark.asyncio
    async def test_embed_with_local_fallback(self):
        """
        🔴 RED: Test que embed usa modelo local si Azure y OpenAI fallan.
        
        Given: Azure y OpenAI fallan
        When: Se llama a embed
        Then: Usa SentenceTransformer local
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_azure.side_effect = Exception("API Error")
            
            with patch('app.services.embedding_service.AsyncOpenAI') as mock_openai:
                mock_openai.side_effect = Exception("API Error")
                
                with patch('app.services.embedding_service.SentenceTransformer') as mock_st:
                    mock_model = MagicMock()
                    mock_model.encode.return_value = [[0.1] * 768]
                    mock_st.return_value = mock_model
                    
                    service = EmbeddingService()
                    embedding = await service.embed("Test text")
                    
                    assert len(embedding) > 0
                    assert service.using_local is True


class TestEmbeddingServiceEmbedBatch:
    """Tests para el método embed_batch."""
    
    @pytest.mark.asyncio
    async def test_embed_batch_multiple_texts(self):
        """
        🔴 RED: Test que embed_batch procesa múltiples textos.
        
        Given: Lista de 3 textos
        When: Se llama a embed_batch
        Then: Retorna 3 embeddings
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1] * 1536),
                MagicMock(embedding=[0.2] * 1536),
                MagicMock(embedding=[0.3] * 1536),
            ]
            mock_client.embeddings.create.return_value = mock_response
            mock_azure.return_value = mock_client
            
            service = EmbeddingService()
            service.using_azure = True
            service.deployment_name = "test-deployment"
            
            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = await service.embed_batch(texts)
            
            assert len(embeddings) == 3
            assert all(len(emb) == 1536 for emb in embeddings)
    
    @pytest.mark.asyncio
    async def test_embed_batch_uses_cache_for_seen_texts(self):
        """
        🔴 RED: Test que embed_batch usa cache para textos ya vistos.
        
        Given: Algunos textos ya en cache
        When: Se llama a embed_batch con textos nuevos y cacheados
        Then: Solo embebe los nuevos
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_azure.return_value = mock_client
            
            service = EmbeddingService()
            service.using_azure = True
            service.deployment_name = "test-deployment"
            
            # Primera llamada cachea "Text 1"
            await service.embed("Text 1")
            
            # Segunda llamada con "Text 1" (cache) y "Text 2" (nuevo)
            embeddings = await service.embed_batch(["Text 1", "Text 2"])
            
            assert len(embeddings) == 2
            # Solo se llama una vez más para "Text 2" (Text 1 estaba en cache)
            assert mock_client.embeddings.create.call_count == 2
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.AsyncAzureOpenAI')
    @patch('app.services.embedding_service.AsyncOpenAI')
    @patch('app.services.embedding_service.settings')
    async def test_embed_batch_handles_empty_list(self, mock_settings, mock_openai_class, mock_azure_class):
        """
        🔴 RED: Test que embed_batch maneja lista vacía.
        
        Given: Lista vacía de textos
        When: Se llama a embed_batch
        Then: Retorna lista vacía sin error
        """
        mock_settings.AZURE_OPENAI_KEY = "test-azure-key"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
        mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_client = AsyncMock()
        mock_azure_class.return_value = mock_client
        
        service = EmbeddingService()
        embeddings = await service.embed_batch([])
        assert embeddings == []


class TestEmbeddingServiceBatching:
    """Tests para batching automático."""
    
    @pytest.mark.asyncio
    async def test_automatic_batching_for_large_input(self):
        """
        🔴 RED: Test que batch grande se divide automáticamente.
        
        Given: 150 textos (más del límite de batch de Azure OpenAI)
        When: Se llama a embed_batch
        Then: Se divide en múltiples llamadas a la API
        """
        with patch('app.services.embedding_service.AsyncAzureOpenAI') as mock_azure:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            # Simular respuesta de Azure OpenAI con embeddings
            mock_response.data = [MagicMock(embedding=[0.1] * 1536) for _ in range(100)]
            mock_client.embeddings.create.return_value = mock_response
            mock_azure.return_value = mock_client
            
            service = EmbeddingService()
            service.using_azure = True
            service.deployment_name = "test-deployment"
            
            # 150 textos deben dividirse en al menos 2 batches
            texts = [f"Text {i}" for i in range(150)]
            embeddings = await service.embed_batch(texts)
            
            assert len(embeddings) == 150
            # Se llamó a la API múltiples veces (batching)
            assert mock_client.embeddings.create.call_count >= 2


class TestEmbeddingServiceLogging:
    """Tests para logging de operaciones."""
    
    @pytest.mark.asyncio
    async def test_logs_embedding_operation(self, caplog):
        """
        🔴 RED: Test que se loguean las operaciones de embedding.
        
        Given: Llamada a embed
        When: Se genera embedding
        Then: Se loguea la operación
        """
        import logging
        
        with patch('app.services.embedding_service.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            service = EmbeddingService()
            service.using_openai = True
            
            with caplog.at_level(logging.DEBUG):
                await service.embed("Test")
                
                # Verificar que se logueó algo sobre embeddings
                assert any("embed" in record.message.lower() for record in caplog.records)


class TestEmbeddingServiceModelSelection:
    """Tests para selección de modelo."""
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.settings')
    async def test_uses_text_embedding_3_large_model(self, mock_settings):
        """
        🔴 RED: Test que usa text-embedding-3-large por defecto.
        
        Given: Configuración por defecto
        When: Se genera embedding
        Then: Usa modelo text-embedding-3-large
        """
        mock_settings.OPENAI_API_KEY = "sk-test"
        
        with patch('app.services.embedding_service.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            service = EmbeddingService()
            service.using_openai = True
            
            await service.embed("Test")
            
            # Verificar que se llamó con el modelo correcto
            call_args = mock_client.embeddings.create.call_args
            assert call_args[1]["model"] == "text-embedding-3-large"

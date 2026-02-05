"""
Tests para RAGService - TDD Red Phase

🔴 RED: Estos tests deben FALLAR primero porque RAGService no existe aún.

El RAGService (Retrieval-Augmented Generation) debe:
1. Recibir un query (pregunta del usuario)
2. Generar embedding del query usando EmbeddingService
3. Buscar documentos similares en Qdrant usando VectorStoreService
4. Construir contexto con los documentos recuperados
5. Generar respuesta usando CopilotService/LLM con el contexto
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# 🔴 RED: Este import DEBE fallar porque no existe el archivo
from app.services.rag_service import RAGService, get_rag_service


class TestRAGServiceInitialization:
    """Tests de inicialización del RAGService."""

    def test_rag_service_can_be_instantiated(self):
        """
        🔴 RED: Test que RAGService se puede instanciar.

        Given: Servicios de dependencias (embedding, vector_store, copilot)
        When: Se instancia RAGService
        Then: El servicio se crea correctamente con las dependencias
        """
        mock_embedding = MagicMock()
        mock_vector_store = MagicMock()
        mock_copilot = MagicMock()

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        assert service is not None
        assert hasattr(service, "search")
        assert hasattr(service, "generate_with_context")
        assert hasattr(service, "query")

    @patch('app.services.embedding_service.get_embedding_service')
    @patch('app.services.copilot_service.get_copilot_service')
    @patch('app.services.rag_service.VectorStoreService')
    def test_singleton_returns_same_instance(self, mock_vector, mock_copilot_func, mock_embedding_func):
        """
        🔴 RED: Test que get_rag_service retorna la misma instancia.

        Given: Llamadas múltiples a get_rag_service
        When: Se llama dos veces
        Then: Retorna la misma instancia (singleton)
        """
        # Mock the services
        mock_embedding_func.return_value = MagicMock()
        mock_copilot_func.return_value = MagicMock()
        mock_vector.return_value = MagicMock()
        
        # Clear any cached instance
        import app.services.rag_service as rag_module
        rag_module._rag_service = None
        
        service1 = get_rag_service()
        service2 = get_rag_service()
        assert service1 is service2


class TestRAGServiceSearch:
    """Tests para el método search (búsqueda de documentos)."""

    @pytest.mark.asyncio
    async def test_search_returns_relevant_documents(self):
        """
        🔴 RED: Test que search retorna documentos relevantes.

        Given: Query "What is SQL injection?" y documentos en la base vectorial
        When: Se ejecuta search con el query
        Then: Retorna lista de documentos con score > 0.7
        """
        # Arrange - Mock dependencies
        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536  # Embedding del query

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "text": "SQL injection is a code injection technique...",
                    "source": "OWASP Top 10",
                    "type": "vulnerability",
                },
            },
            {
                "id": "doc2",
                "score": 0.88,
                "metadata": {
                    "text": "To prevent SQL injection, use parameterized queries...",
                    "source": "Security Best Practices",
                    "type": "mitigation",
                },
            },
        ]

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        # Act
        results = await service.search("What is SQL injection?", limit=5)

        # Assert
        assert len(results) == 2
        assert results[0]["score"] == 0.95
        assert "SQL injection" in results[0]["metadata"]["text"]
        assert results[1]["score"] == 0.88

        # Verify mock calls
        mock_embedding.embed.assert_called_once_with("What is SQL injection?")
        mock_vector_store.search_similar.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_no_results_returns_empty(self):
        """
        🔴 RED: Test que search retorna lista vacía cuando no hay resultados.

        Given: Query que no tiene documentos similares en la BD
        When: Se ejecuta search
        Then: Retorna lista vacía sin error
        """
        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = []  # Sin resultados

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        results = await service.search("Some unknown query")

        assert results == []
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_filters_applies_metadata_filters(self):
        """
        🔴 RED: Test que search aplica filtros de metadata correctamente.

        Given: Query con filtros de metadata (ej: source="OWASP")
        When: Se ejecuta search con filters parameter
        Then: Los filtros se pasan a vector_store.search_similar
        """
        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {"source": "OWASP Top 10", "text": "SQL injection..."},
            }
        ]

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        filters = {"source": "OWASP Top 10"}
        results = await service.search("SQL injection", filters=filters)

        assert len(results) == 1
        mock_vector_store.search_similar.assert_called_once_with(
            query_vector=[0.1] * 1536, limit=10, filters=filters
        )


class TestRAGServiceContextBuilding:
    """Tests para la construcción de contexto desde documentos."""

    @pytest.mark.asyncio
    async def test_build_context_from_documents(self):
        """
        🔴 RED: Test que build_context construye contexto correctamente.

        Given: Lista de documentos con metadata
        When: Se llama a build_context
        Then: Retorna string formateado con los documentos y sus fuentes
        """
        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        documents = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "text": "SQL injection is a vulnerability...",
                    "source": "OWASP Top 10",
                },
            },
            {
                "id": "doc2",
                "score": 0.88,
                "metadata": {
                    "text": "Use parameterized queries to prevent SQL injection...",
                    "source": "Security Best Practices",
                },
            },
        ]

        context = service.build_context(documents)

        assert isinstance(context, str)
        assert "SQL injection is a vulnerability" in context
        assert "Use parameterized queries" in context
        assert "OWASP Top 10" in context
        assert "Security Best Practices" in context

    @pytest.mark.asyncio
    async def test_context_building_respects_token_limit(self):
        """
        🔴 RED: Test que build_context respeta el límite de tokens.

        Given: Lista de 10 documentos grandes (muchos tokens)
        When: Se llama a build_context con max_tokens=500
        Then: El contexto resultante no excede el límite de tokens
        """
        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        # Documentos grandes
        documents = [
            {
                "id": f"doc{i}",
                "score": 0.9,
                "metadata": {"text": "A" * 1000, "source": f"Source {i}"},  # 1000 chars
            }
            for i in range(10)
        ]

        context = service.build_context(documents, max_tokens=500)

        # Aproximación: 1 token ≈ 4 caracteres
        # 500 tokens ≈ 2000 caracteres
        assert len(context) < 2500  # Margen de seguridad
        assert len(context) > 0  # No debe estar vacío

    @pytest.mark.asyncio
    async def test_build_context_handles_empty_documents(self):
        """
        🔴 RED: Test que build_context maneja lista vacía de documentos.

        Given: Lista vacía de documentos
        When: Se llama a build_context
        Then: Retorna string indicando que no hay contexto disponible
        """
        service = RAGService(
            embedding_service=MagicMock(),
            vector_store_service=MagicMock(),
            copilot_service=MagicMock(),
        )

        context = service.build_context([])

        assert isinstance(context, str)
        assert len(context) > 0
        assert ("no context" in context.lower() 
                or "no documents" in context.lower() 
                or "no relevant" in context.lower())


class TestRAGServiceGeneration:
    """Tests para la generación de respuestas con LLM."""

    @pytest.mark.asyncio
    async def test_generate_with_context_calls_llm(self):
        """
        🔴 RED: Test que generate_with_context llama al LLM correctamente.

        Given: Query y contexto construido
        When: Se llama a generate_with_context
        Then: Llama a copilot_service.chat con prompt que incluye el contexto
        """
        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()
        mock_copilot = AsyncMock()

        # Mock copilot session y response
        mock_session = MagicMock()
        mock_copilot.create_session.return_value = mock_session
        mock_copilot.chat.return_value = {
            "text": "SQL injection is a security vulnerability where...",
            "model": "claude-sonnet-4.5",
            "provider": "github-copilot-sdk",
            "tokens": 150,
        }

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        query = "What is SQL injection?"
        context = "Context: SQL injection is a code injection technique..."

        response = await service.generate_with_context(query, context)

        assert response["text"] == "SQL injection is a security vulnerability where..."
        assert response["model"] == "claude-sonnet-4.5"
        assert response["tokens"] == 150

        # Verify LLM was called
        mock_copilot.create_session.assert_called_once()
        mock_copilot.chat.assert_called_once()

        # Verify the prompt includes both query and context
        call_args = mock_copilot.chat.call_args
        prompt_used = call_args[0][1]  # Second argument to chat()
        assert query in prompt_used or context in prompt_used

    @pytest.mark.asyncio
    async def test_generate_with_context_uses_system_prompt(self):
        """
        🔴 RED: Test que generate_with_context usa un system prompt específico.

        Given: Query y contexto
        When: Se crea la sesión con copilot
        Then: Se usa un system prompt que indica el rol de CISO Assistant
        """
        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()
        mock_copilot = AsyncMock()

        mock_session = MagicMock()
        mock_copilot.create_session.return_value = mock_session
        mock_copilot.chat.return_value = {
            "text": "Response",
            "model": "claude-sonnet-4.5",
            "provider": "github-copilot-sdk",
            "tokens": 100,
        }

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        await service.generate_with_context("Test query", "Test context")

        # Verify create_session was called with system_prompt
        mock_copilot.create_session.assert_called_once()
        call_args = mock_copilot.create_session.call_args
        system_prompt = call_args[1].get("system_prompt", "")

        assert len(system_prompt) > 0
        assert "security" in system_prompt.lower() or "ciso" in system_prompt.lower()


class TestRAGServiceQuery:
    """Tests para el método query (end-to-end RAG)."""

    @pytest.mark.asyncio
    async def test_query_performs_full_rag_pipeline(self):
        """
        🔴 RED: Test que query ejecuta el pipeline RAG completo.

        Given: Query del usuario
        When: Se ejecuta query()
        Then: Ejecuta: embed → search → build_context → generate
        """
        # Arrange - Mock all dependencies
        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "text": "SQL injection is a vulnerability...",
                    "source": "OWASP",
                },
            }
        ]

        mock_copilot = AsyncMock()
        mock_session = MagicMock()
        mock_copilot.create_session.return_value = mock_session
        mock_copilot.chat.return_value = {
            "text": "SQL injection is a security vulnerability...",
            "model": "claude-sonnet-4.5",
            "provider": "github-copilot-sdk",
            "tokens": 200,
        }

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        # Act
        result = await service.query("What is SQL injection?")

        # Assert - Verify full pipeline executed
        assert result["answer"] is not None
        assert result["sources"] is not None
        assert len(result["sources"]) > 0
        assert result["model"] == "claude-sonnet-4.5"

        # Verify all steps were called
        mock_embedding.embed.assert_called_once()
        mock_vector_store.search_similar.assert_called_once()
        mock_copilot.create_session.assert_called_once()
        mock_copilot.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_with_no_documents_still_generates_answer(self):
        """
        🔴 RED: Test que query genera respuesta incluso sin documentos.

        Given: Query sin documentos similares en la BD
        When: Se ejecuta query()
        Then: Genera respuesta con el LLM sin contexto adicional
        """
        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = []  # Sin documentos

        mock_copilot = AsyncMock()
        mock_session = MagicMock()
        mock_copilot.create_session.return_value = mock_session
        mock_copilot.chat.return_value = {
            "text": "I don't have specific documents about that...",
            "model": "claude-sonnet-4.5",
            "provider": "github-copilot-sdk",
            "tokens": 50,
        }

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        result = await service.query("Some unknown topic")

        assert result["answer"] is not None
        assert result["sources"] == []
        assert len(result["answer"]) > 0
        mock_copilot.chat.assert_called_once()


class TestRAGServiceValidation:
    """Tests para validación de inputs."""

    @pytest.mark.asyncio
    async def test_empty_query_raises_validation_error(self):
        """
        🔴 RED: Test que query vacío lanza ValidationError.

        Given: Query vacío o solo espacios
        When: Se ejecuta query("") o query("   ")
        Then: Lanza ValueError con mensaje descriptivo
        """
        service = RAGService(
            embedding_service=MagicMock(),
            vector_store_service=MagicMock(),
            copilot_service=MagicMock(),
        )

        with pytest.raises(ValueError, match="Query cannot be empty"):
            await service.query("")

        with pytest.raises(ValueError, match="Query cannot be empty"):
            await service.query("   ")

    @pytest.mark.asyncio
    async def test_search_with_invalid_limit_raises_error(self):
        """
        🔴 RED: Test que limit inválido lanza ValueError.

        Given: limit <= 0 o limit > 100
        When: Se ejecuta search con limit inválido
        Then: Lanza ValueError
        """
        service = RAGService(
            embedding_service=MagicMock(),
            vector_store_service=MagicMock(),
            copilot_service=MagicMock(),
        )

        with pytest.raises(ValueError, match="limit must be between 1 and 100"):
            await service.search("test query", limit=0)

        with pytest.raises(ValueError, match="limit must be between 1 and 100"):
            await service.search("test query", limit=-5)

        with pytest.raises(ValueError, match="limit must be between 1 and 100"):
            await service.search("test query", limit=150)


class TestRAGServiceLogging:
    """Tests para verificar logging adecuado."""

    @pytest.mark.asyncio
    async def test_logs_search_operation(self, caplog):
        """
        🔴 RED: Test que search registra operación en logs.

        Given: Query válido
        When: Se ejecuta search
        Then: Se registra en logs la búsqueda y número de resultados
        """
        import logging

        caplog.set_level(logging.INFO)

        mock_embedding = AsyncMock()
        mock_embedding.embed.return_value = [0.1] * 1536

        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = [
            {"id": "doc1", "score": 0.95, "metadata": {"text": "Test"}}
        ]

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=MagicMock(),
        )

        await service.search("Test query")

        # Verify logs contain search information
        assert any("search" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_logs_generation_with_token_count(self, caplog):
        """
        🔴 RED: Test que generate_with_context registra tokens usados.

        Given: Query y contexto
        When: Se ejecuta generate_with_context
        Then: Se registra en logs el número de tokens consumidos
        """
        import logging

        caplog.set_level(logging.INFO)

        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()
        mock_copilot = AsyncMock()

        mock_session = MagicMock()
        mock_copilot.create_session.return_value = mock_session
        mock_copilot.chat.return_value = {
            "text": "Response",
            "model": "claude-sonnet-4.5",
            "provider": "github-copilot-sdk",
            "tokens": 250,
        }

        service = RAGService(
            embedding_service=mock_embedding,
            vector_store_service=mock_vector_store,
            copilot_service=mock_copilot,
        )

        await service.generate_with_context("Query", "Context")

        # Verify logs contain token information
        assert any("token" in record.message.lower() for record in caplog.records)

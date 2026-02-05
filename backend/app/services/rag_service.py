"""
RAG Service (Retrieval-Augmented Generation).

🟢 GREEN PHASE: Implementación mínima para pasar los tests.

El RAGService coordina el pipeline RAG completo:
1. Embedding del query usando EmbeddingService
2. Búsqueda de documentos similares en VectorStoreService
3. Construcción de contexto desde los documentos
4. Generación de respuesta con LLM (CopilotService)
"""

import logging
from typing import Any

from app.services.copilot_service import CopilotService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService


logger = logging.getLogger(__name__)


class RAGService:
    """
    Servicio para Retrieval-Augmented Generation (RAG).

    Coordina el pipeline completo de RAG para responder preguntas del usuario
    usando documentos de la base de conocimiento vectorial.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store_service: VectorStoreService,
        copilot_service: CopilotService,
    ):
        """
        Inicializa el RAGService con sus dependencias.

        Args:
            embedding_service: Servicio para generar embeddings
            vector_store_service: Servicio para búsqueda vectorial
            copilot_service: Servicio LLM para generar respuestas
        """
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service
        self.copilot_service = copilot_service
        self.system_prompt = """You are a CISO Digital Assistant, an AI expert in cybersecurity and information security.

Your role is to help security professionals with:
- Risk assessment and management
- Security compliance (ISO 27001, NIST, PCI-DSS, etc.)
- Incident response guidance
- Security best practices and recommendations
- Vulnerability analysis and remediation

When answering:
1. Be precise and technical when needed
2. Cite sources from the provided context
3. If you don't know something, say so clearly
4. Prioritize security and compliance in your recommendations
5. Use clear, professional language

Always base your answers on the provided context when available."""

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca documentos similares al query en la base vectorial.

        Args:
            query: Pregunta o texto de búsqueda
            limit: Número máximo de resultados (default: 10, max: 100)
            filters: Filtros opcionales de metadata

        Returns:
            Lista de documentos con score y metadata

        Raises:
            ValueError: Si limit está fuera del rango 1-100

        Example:
            >>> results = await rag_service.search("What is SQL injection?", limit=5)
            >>> for result in results:
            ...     print(f"Score: {result['score']}, Text: {result['metadata']['text']}")
        """
        # Validar limit
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        logger.info(f"Searching for query: {query[:50]}... (limit={limit})")

        # 1. Generar embedding del query
        query_embedding = await self.embedding_service.embed(query)

        # 2. Buscar documentos similares
        results = await self.vector_store_service.search_similar(
            query_vector=query_embedding,
            limit=limit,
            filters=filters,
        )

        logger.info(f"Found {len(results)} documents for query")

        return results

    def build_context(
        self,
        documents: list[dict[str, Any]],
        max_tokens: int = 4000,
    ) -> str:
        """
        Construye contexto formateado desde los documentos recuperados.

        Args:
            documents: Lista de documentos con metadata
            max_tokens: Límite máximo de tokens para el contexto

        Returns:
            String con contexto formateado para el LLM

        Example:
            >>> documents = [{"id": "doc1", "score": 0.95, "metadata": {"text": "...", "source": "OWASP"}}]
            >>> context = rag_service.build_context(documents)
            >>> print(context)
        """
        if not documents:
            return "No relevant documents found in the knowledge base."

        # Aproximación: 1 token ≈ 4 caracteres
        max_chars = max_tokens * 4

        context_parts = ["# Relevant Information from Knowledge Base\n"]
        current_length = len(context_parts[0])

        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            text = metadata.get("text", "")
            source = metadata.get("source", "Unknown")
            score = doc.get("score", 0.0)

            # Formatear documento
            doc_text = f"\n## Document {i} (Relevance: {score:.2f})\n"
            doc_text += f"**Source:** {source}\n"
            doc_text += f"**Content:** {text}\n"

            # Verificar límite de tokens
            if current_length + len(doc_text) > max_chars:
                logger.info(
                    f"Reached token limit, including {i-1} of {len(documents)} documents"
                )
                break

            context_parts.append(doc_text)
            current_length += len(doc_text)

        context = "".join(context_parts)
        logger.info(f"Built context with {len(context)} characters from {len(context_parts)-1} documents")

        return context

    async def generate_with_context(
        self,
        query: str,
        context: str,
    ) -> dict[str, Any]:
        """
        Genera respuesta usando el LLM con el contexto proporcionado.

        Args:
            query: Pregunta del usuario
            context: Contexto construido desde documentos

        Returns:
            Dict con la respuesta del LLM

        Example:
            >>> response = await rag_service.generate_with_context(
            ...     "What is SQL injection?",
            ...     "Context: SQL injection is..."
            ... )
            >>> print(response["text"])
        """
        logger.info(f"Generating response for query: {query[:50]}...")

        # Construir prompt con contexto
        prompt = f"""{context}

---

**User Question:** {query}

Based on the information provided above, please answer the user's question. If the context doesn't contain relevant information, say so and provide general guidance if appropriate."""

        # Crear sesión con system prompt
        session = await self.copilot_service.create_session(
            model="claude-sonnet-4.5",
            system_prompt=self.system_prompt,
        )

        # Generar respuesta
        response = await self.copilot_service.chat(session, prompt)

        logger.info(
            f"Generated response - Model: {response.get('model')}, "
            f"Tokens: {response.get('tokens', 0)}"
        )

        return response

    async def query(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ejecuta el pipeline RAG completo: search → build_context → generate.

        Args:
            query: Pregunta del usuario
            limit: Número máximo de documentos a recuperar
            filters: Filtros opcionales de metadata

        Returns:
            Dict con answer, sources, model usado, etc.

        Raises:
            ValueError: Si el query está vacío

        Example:
            >>> result = await rag_service.query("What is SQL injection?")
            >>> print(result["answer"])
            >>> print(f"Sources: {len(result['sources'])}")
        """
        # Validar query
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.info(f"Starting RAG query: {query[:100]}...")

        # 1. Search - Buscar documentos relevantes
        documents = await self.search(query, limit=limit, filters=filters)

        # 2. Build Context - Construir contexto desde documentos
        context = self.build_context(documents)

        # 3. Generate - Generar respuesta con LLM
        response = await self.generate_with_context(query, context)

        # 4. Construir resultado final
        result = {
            "answer": response.get("text", ""),
            "sources": documents,
            "model": response.get("model", ""),
            "provider": response.get("provider", ""),
            "tokens": response.get("tokens", 0),
            "num_sources": len(documents),
        }

        logger.info(
            f"RAG query completed - {result['num_sources']} sources, "
            f"{result['tokens']} tokens used"
        )

        return result


# Singleton instance
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """
    Retorna la instancia singleton del RAGService.

    Returns:
        RAGService: La instancia singleton

    Example:
        >>> rag_service = get_rag_service()
        >>> result = await rag_service.query("What is phishing?")
    """
    global _rag_service
    if _rag_service is None:
        # Importar servicios necesarios
        from app.core.config import settings
        from app.services.copilot_service import get_copilot_service
        from app.services.embedding_service import get_embedding_service

        embedding_service = get_embedding_service()
        copilot_service = get_copilot_service()

        # VectorStoreService requiere inicialización manual
        vector_store_service = VectorStoreService(
            qdrant_url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name="security_knowledge",
        )

        _rag_service = RAGService(
            embedding_service=embedding_service,
            vector_store_service=vector_store_service,
            copilot_service=copilot_service,
        )

    return _rag_service

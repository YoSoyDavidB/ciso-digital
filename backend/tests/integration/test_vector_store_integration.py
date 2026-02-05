"""
Integration test for VectorStoreService with actual Qdrant instance.

Este test verifica que podemos conectarnos a Qdrant y realizar operaciones reales.
Requiere que Qdrant esté corriendo en Docker.
"""

import pytest

from app.core.config import settings
from app.services.vector_store import VectorStoreService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_vector_store_integration_with_qdrant():
    """
    Test de integración: conectar a Qdrant real y crear colección.

    Given: Qdrant corriendo en Docker
    When: Creamos VectorStoreService y llamamos ensure_collection
    Then: La colección debe crearse exitosamente
    """
    # Arrange
    service = VectorStoreService(
        qdrant_url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name="test_integration_collection",
    )

    try:
        # Act - Crear colección
        await service.ensure_collection(vector_size=1536, distance="Cosine")

        # Assert - Verificar que la colección existe
        info = await service.get_collection_info()
        assert info["vectors_count"] == 0  # Colección vacía recién creada
        assert info["status"] in ["GREEN", "YELLOW", "RED"]

        # Test insert y search
        embeddings = [[0.1] * 1536, [0.2] * 1536]  # 1536-dim vectors
        metadata = [
            {"source": "test1.pdf", "page": 1},
            {"source": "test2.pdf", "page": 2},
        ]

        # Insert
        result = await service.insert_embeddings(embeddings, metadata)
        assert result is True

        # Search
        query_vector = [0.1] * 1536
        results = await service.search_similar(query_vector, limit=2)
        assert len(results) == 2
        # Verificar que ambos documentos están en los resultados
        sources = [r["metadata"]["source"] for r in results]
        assert "test1.pdf" in sources
        assert "test2.pdf" in sources

    finally:
        # Cleanup - eliminar la colección de test
        await service.client.delete_collection("test_integration_collection")
        await service.close()

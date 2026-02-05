"""
Tests para VectorStoreService - Cliente de Qdrant.

Tests unitarios para el servicio de almacenamiento vectorial usando Qdrant.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# =============================================================================
# Tests para VectorStoreService
# =============================================================================


@pytest.mark.asyncio
async def test_vector_store_service_initialization():
    """
    🔴 RED: Test que VectorStoreService se inicializa correctamente.

    Given: Parámetros de configuración válidos
    When: Se crea una instancia de VectorStoreService
    Then: El servicio debe tener un cliente Qdrant configurado
    """
    from app.services.vector_store import VectorStoreService

    # Arrange & Act
    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        api_key=None,
        collection_name="test_collection",
    )

    # Assert
    assert service is not None
    assert service.collection_name == "test_collection"
    assert service.qdrant_url == "http://localhost:6333"


@pytest.mark.asyncio
async def test_ensure_collection_creates_collection_if_not_exists():
    """
    🔴 RED: Test que ensure_collection crea colección si no existe.

    Given: Una colección que no existe en Qdrant
    When: Se llama a ensure_collection
    Then: Debe crear la colección con la configuración correcta
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_client.collection_exists.return_value = False
    mock_client.create_collection = AsyncMock()

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    # Act
    await service.ensure_collection(vector_size=1536, distance="Cosine")

    # Assert
    mock_client.collection_exists.assert_called_once_with("security_knowledge")
    mock_client.create_collection.assert_called_once()
    # Verificar parámetros de create_collection
    call_kwargs = mock_client.create_collection.call_args[1]
    assert call_kwargs["collection_name"] == "security_knowledge"
    assert call_kwargs["vectors_config"].size == 1536
    assert call_kwargs["vectors_config"].distance.name == "COSINE"


@pytest.mark.asyncio
async def test_ensure_collection_skips_if_exists():
    """
    🔴 RED: Test que ensure_collection no crea colección si ya existe.

    Given: Una colección que ya existe en Qdrant
    When: Se llama a ensure_collection
    Then: No debe intentar crear la colección nuevamente
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_client.collection_exists.return_value = True
    mock_client.create_collection = AsyncMock()

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    # Act
    await service.ensure_collection(vector_size=1536)

    # Assert
    mock_client.collection_exists.assert_called_once()
    mock_client.create_collection.assert_not_called()


@pytest.mark.asyncio
async def test_insert_embeddings():
    """
    🔴 RED: Test que insert_embeddings inserta vectores en Qdrant.

    Given: Una lista de vectores con sus metadatos
    When: Se llama a insert_embeddings
    Then: Los vectores deben insertarse en la colección
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_client.upsert = AsyncMock()

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    embeddings = [
        [0.1, 0.2, 0.3],  # Vector 1
        [0.4, 0.5, 0.6],  # Vector 2
    ]
    metadata = [
        {"source": "doc1.pdf", "page": 1},
        {"source": "doc2.pdf", "page": 5},
    ]
    ids = ["id-1", "id-2"]

    # Act
    result = await service.insert_embeddings(embeddings=embeddings, metadata=metadata, ids=ids)

    # Assert
    mock_client.upsert.assert_called_once()
    call_kwargs = mock_client.upsert.call_args[1]
    assert call_kwargs["collection_name"] == "security_knowledge"
    assert len(call_kwargs["points"]) == 2
    assert result is True


@pytest.mark.asyncio
async def test_search_similar_vectors():
    """
    🔴 RED: Test que search_similar busca vectores similares.

    Given: Un vector de consulta
    When: Se llama a search_similar
    Then: Debe retornar los vectores más similares con sus scores
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()

    # Mock de resultados de búsqueda (nueva API con .points)
    mock_result_1 = MagicMock()
    mock_result_1.id = "id-1"
    mock_result_1.score = 0.95
    mock_result_1.payload = {"source": "doc1.pdf", "page": 1}

    mock_result_2 = MagicMock()
    mock_result_2.id = "id-2"
    mock_result_2.score = 0.87
    mock_result_2.payload = {"source": "doc2.pdf", "page": 5}

    mock_response = MagicMock()
    mock_response.points = [mock_result_1, mock_result_2]
    mock_client.query_points.return_value = mock_response

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    query_vector = [0.1, 0.2, 0.3]

    # Act
    results = await service.search_similar(query_vector=query_vector, limit=2)

    # Assert
    mock_client.query_points.assert_called_once()
    call_kwargs = mock_client.query_points.call_args[1]
    assert call_kwargs["collection_name"] == "security_knowledge"
    assert call_kwargs["query"] == query_vector
    assert call_kwargs["limit"] == 2

    # Verificar resultados
    assert len(results) == 2
    assert results[0]["id"] == "id-1"
    assert results[0]["score"] == 0.95
    assert results[0]["metadata"]["source"] == "doc1.pdf"


@pytest.mark.asyncio
async def test_search_similar_with_filter():
    """
    🔴 RED: Test que search_similar soporta filtros en metadata.

    Given: Un vector de consulta y filtros de metadata
    When: Se llama a search_similar con filtros
    Then: Debe aplicar los filtros en la búsqueda
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.points = []
    mock_client.query_points.return_value = mock_response

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    query_vector = [0.1, 0.2, 0.3]
    filters = {"source": "doc1.pdf"}

    # Act
    await service.search_similar(query_vector=query_vector, limit=5, filters=filters)

    # Assert
    mock_client.query_points.assert_called_once()
    call_kwargs = mock_client.query_points.call_args[1]
    assert call_kwargs["query_filter"] is not None


@pytest.mark.asyncio
async def test_delete_embeddings():
    """
    🔴 RED: Test que delete_embeddings elimina vectores por IDs.

    Given: Una lista de IDs de vectores
    When: Se llama a delete_embeddings
    Then: Los vectores deben eliminarse de la colección
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_client.delete = AsyncMock()

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    ids_to_delete = ["id-1", "id-2", "id-3"]

    # Act
    result = await service.delete_embeddings(ids=ids_to_delete)

    # Assert
    mock_client.delete.assert_called_once()
    call_kwargs = mock_client.delete.call_args[1]
    assert call_kwargs["collection_name"] == "security_knowledge"
    assert result is True


@pytest.mark.asyncio
async def test_get_collection_info():
    """
    🔴 RED: Test que get_collection_info retorna información de la colección.

    Given: Una colección existente
    When: Se llama a get_collection_info
    Then: Debe retornar información sobre la colección (count, config, etc.)
    """
    from app.services.vector_store import VectorStoreService

    # Arrange
    mock_client = AsyncMock()
    mock_info = MagicMock()
    mock_info.indexed_vectors_count = 1000
    mock_info.points_count = 1000
    mock_status = MagicMock()
    mock_status.name = "GREEN"
    mock_info.status = mock_status
    mock_client.get_collection.return_value = mock_info

    service = VectorStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="security_knowledge",
    )
    service.client = mock_client

    # Act
    info = await service.get_collection_info()

    # Assert
    mock_client.get_collection.assert_called_once_with("security_knowledge")
    assert info["vectors_count"] == 1000
    assert info["points_count"] == 1000
    assert info["status"] == "GREEN"

"""
Vector Store Service - Cliente para Qdrant.

Servicio para gestionar almacenamiento y búsqueda de embeddings vectoriales
usando Qdrant como base de datos vectorial.
"""

import uuid
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class VectorStoreService:
    """
    Servicio para gestionar embeddings vectoriales en Qdrant.

    Proporciona métodos para crear colecciones, insertar embeddings,
    buscar vectores similares y gestionar la base de datos vectorial.
    """

    def __init__(
        self,
        qdrant_url: str,
        api_key: str | None = None,
        collection_name: str = "security_knowledge",
    ):
        """
        Inicializa el cliente de Qdrant.

        Args:
            qdrant_url: URL del servidor Qdrant (ej: http://localhost:6333)
            api_key: API key opcional para autenticación
            collection_name: Nombre de la colección a usar

        Example:
            >>> service = VectorStoreService(
            ...     qdrant_url="http://localhost:6333",
            ...     collection_name="security_knowledge"
            ... )
        """
        self.qdrant_url = qdrant_url
        self.api_key = api_key
        self.collection_name = collection_name

        # Inicializar cliente asíncrono
        self.client = AsyncQdrantClient(
            url=qdrant_url,
            api_key=api_key,
        )

    async def ensure_collection(
        self,
        vector_size: int = 1536,
        distance: str = "Cosine",
    ) -> None:
        """
        Asegura que la colección existe, creándola si no existe.

        Args:
            vector_size: Dimensión de los vectores (default: 1536 para OpenAI)
            distance: Métrica de distancia: "Cosine", "Euclid", o "Dot"

        Raises:
            ValueError: Si distance no es válido

        Example:
            >>> await service.ensure_collection(vector_size=1536)
        """
        # Verificar si la colección existe
        exists = await self.client.collection_exists(self.collection_name)

        if exists:
            return

        # Mapear string a Distance enum
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclid": Distance.EUCLID,
            "Dot": Distance.DOT,
        }

        if distance not in distance_map:
            raise ValueError(
                f"Invalid distance: {distance}. Must be one of {list(distance_map.keys())}"
            )

        # Crear colección con configuración de vectores
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance_map[distance]),
        )

    async def insert_embeddings(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> bool:
        """
        Inserta embeddings con sus metadatos en la colección.

        Args:
            embeddings: Lista de vectores a insertar
            metadata: Lista de metadatos asociados a cada vector
            ids: IDs opcionales para los puntos (se generan UUID si no se proveen)

        Returns:
            bool: True si la inserción fue exitosa

        Raises:
            ValueError: Si las listas no tienen la misma longitud

        Example:
            >>> embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            >>> metadata = [{"source": "doc1.pdf"}, {"source": "doc2.pdf"}]
            >>> await service.insert_embeddings(embeddings, metadata)
        """
        if len(embeddings) != len(metadata):
            raise ValueError("embeddings and metadata must have the same length")

        # Generar IDs si no se proveen
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in embeddings]

        if len(ids) != len(embeddings):
            raise ValueError("ids, embeddings and metadata must have the same length")

        # Crear puntos para insertar
        points = [
            PointStruct(id=point_id, vector=vector, payload=meta)
            for point_id, vector, meta in zip(ids, embeddings, metadata, strict=True)
        ]

        # Insertar en Qdrant
        await self.client.upsert(collection_name=self.collection_name, points=points)

        return True

    async def search_similar(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca vectores similares al query vector.

        Args:
            query_vector: Vector de consulta
            limit: Número máximo de resultados
            filters: Filtros opcionales sobre metadata

        Returns:
            List[Dict]: Lista de resultados con id, score y metadata

        Example:
            >>> query = [0.1, 0.2, 0.3]
            >>> results = await service.search_similar(query, limit=5)
            >>> for result in results:
            ...     print(f"ID: {result['id']}, Score: {result['score']}")
        """
        # Construir filtro si se proporciona
        query_filter = None
        if filters:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filters.items()
            ]
            query_filter = Filter(must=conditions)

        # Realizar búsqueda con query_points (nueva API)
        search_result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

        # Formatear resultados
        results = [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.payload,
            }
            for hit in search_result.points
        ]

        return results

    async def delete_embeddings(self, ids: list[str]) -> bool:
        """
        Elimina embeddings por sus IDs.

        Args:
            ids: Lista de IDs de puntos a eliminar

        Returns:
            bool: True si la eliminación fue exitosa

        Example:
            >>> await service.delete_embeddings(["id-1", "id-2"])
        """
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )

        return True

    async def get_collection_info(self) -> dict[str, Any]:
        """
        Obtiene información sobre la colección.

        Returns:
            Dict con información de la colección (count, status, etc.)

        Example:
            >>> info = await service.get_collection_info()
            >>> print(f"Vectors: {info['vectors_count']}")
        """
        collection = await self.client.get_collection(self.collection_name)

        return {
            "vectors_count": collection.indexed_vectors_count or 0,
            "points_count": collection.points_count,
            "status": collection.status.name if collection.status else "unknown",
        }

    async def close(self) -> None:
        """
        Cierra la conexión al cliente de Qdrant.

        Example:
            >>> await service.close()
        """
        await self.client.close()

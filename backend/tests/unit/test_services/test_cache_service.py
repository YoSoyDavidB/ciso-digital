"""
Tests para CacheService - Cliente de Redis.

Tests unitarios para el servicio de caché usando Redis.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# =============================================================================
# Tests para CacheService
# =============================================================================


@pytest.mark.asyncio
async def test_cache_service_initialization():
    """
    🔴 RED: Test que CacheService se inicializa correctamente.

    Given: Una URL de Redis válida
    When: Se crea una instancia de CacheService
    Then: El servicio debe tener un cliente Redis configurado
    """
    from app.services.cache_service import CacheService

    # Arrange & Act
    service = CacheService(redis_url="redis://localhost:6379/0")

    # Assert
    assert service is not None
    assert service.redis_url == "redis://localhost:6379/0"


@pytest.mark.asyncio
async def test_cache_service_get_existing_key():
    """
    🔴 RED: Test que get() retorna el valor de una clave existente.

    Given: Una clave que existe en Redis
    When: Se llama a get(key)
    Then: Debe retornar el valor almacenado
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.get.return_value = b"test_value"
    service.client = mock_client

    # Act
    result = await service.get("test_key")

    # Assert
    mock_client.get.assert_called_once_with("test_key")
    assert result == "test_value"


@pytest.mark.asyncio
async def test_cache_service_get_nonexistent_key():
    """
    🔴 RED: Test que get() retorna None para clave inexistente.

    Given: Una clave que no existe en Redis
    When: Se llama a get(key)
    Then: Debe retornar None
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    service.client = mock_client

    # Act
    result = await service.get("nonexistent_key")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_cache_service_set_with_default_ttl():
    """
    🔴 RED: Test que set() almacena un valor con TTL por defecto.

    Given: Una clave y valor
    When: Se llama a set(key, value) sin especificar TTL
    Then: Debe almacenar con TTL de 300 segundos por defecto
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    service.client = mock_client

    # Act
    await service.set("test_key", "test_value")

    # Assert
    mock_client.setex.assert_called_once_with("test_key", 300, "test_value")


@pytest.mark.asyncio
async def test_cache_service_set_with_custom_ttl():
    """
    🔴 RED: Test que set() almacena un valor con TTL personalizado.

    Given: Una clave, valor y TTL personalizado
    When: Se llama a set(key, value, ttl=600)
    Then: Debe almacenar con el TTL especificado
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    service.client = mock_client

    # Act
    await service.set("test_key", "test_value", ttl=600)

    # Assert
    mock_client.setex.assert_called_once_with("test_key", 600, "test_value")


@pytest.mark.asyncio
async def test_cache_service_delete():
    """
    🔴 RED: Test que delete() elimina una clave.

    Given: Una clave existente en Redis
    When: Se llama a delete(key)
    Then: Debe eliminar la clave
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.delete.return_value = 1  # 1 = deleted
    service.client = mock_client

    # Act
    result = await service.delete("test_key")

    # Assert
    mock_client.delete.assert_called_once_with("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_service_exists_true():
    """
    🔴 RED: Test que exists() retorna True si la clave existe.

    Given: Una clave que existe en Redis
    When: Se llama a exists(key)
    Then: Debe retornar True
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.exists.return_value = 1  # 1 = exists
    service.client = mock_client

    # Act
    result = await service.exists("test_key")

    # Assert
    mock_client.exists.assert_called_once_with("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_service_exists_false():
    """
    🔴 RED: Test que exists() retorna False si la clave no existe.

    Given: Una clave que no existe en Redis
    When: Se llama a exists(key)
    Then: Debe retornar False
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.exists.return_value = 0  # 0 = does not exist
    service.client = mock_client

    # Act
    result = await service.exists("nonexistent_key")

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_cache_service_handles_redis_connection_error():
    """
    🔴 RED: Test que el servicio maneja errores de conexión a Redis.

    Given: Redis no está disponible
    When: Se intenta get() y falla la conexión
    Then: Debe loggear warning y retornar None sin crash
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection refused")
    service.client = mock_client

    # Act (no debe lanzar excepción)
    result = await service.get("test_key")

    # Assert
    assert result is None  # Debe retornar None en caso de error


@pytest.mark.asyncio
async def test_cached_decorator_caches_function_result():
    """
    🔴 RED: Test que el decorator @cached() cachea resultados de funciones.

    Given: Una función decorada con @cached()
    When: Se llama la función múltiples veces con los mismos argumentos
    Then: Debe ejecutarse solo una vez y retornar el valor cacheado
    """
    from app.services.cache_service import CacheService, cached

    # Arrange
    mock_service = AsyncMock(spec=CacheService)
    mock_service.get.return_value = None  # Primera llamada: cache miss
    mock_service.set = AsyncMock()

    call_count = 0

    @cached(ttl=60, cache_service=mock_service)
    async def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # Act - Primera llamada (cache miss)
    result1 = await expensive_function(5)

    # Assert
    assert result1 == 10
    assert call_count == 1
    mock_service.get.assert_called_once()
    mock_service.set.assert_called_once()


@pytest.mark.asyncio
async def test_cached_decorator_returns_cached_value():
    """
    🔴 RED: Test que @cached() retorna valor cacheado en segunda llamada.

    Given: Una función ya ejecutada con un valor en caché
    When: Se llama nuevamente con los mismos argumentos
    Then: Debe retornar el valor cacheado sin ejecutar la función
    """
    from app.services.cache_service import CacheService, cached

    # Arrange
    mock_service = AsyncMock(spec=CacheService)
    # Segunda llamada: cache hit (retorna valor cacheado)
    mock_service.get.return_value = "20"  # Valor en string como viene de Redis

    call_count = 0

    @cached(ttl=60, cache_service=mock_service)
    async def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # Act - Segunda llamada (cache hit)
    result = await expensive_function(10)

    # Assert
    assert result == "20"  # Retorna el valor del cache (string)
    assert call_count == 0  # La función NO se ejecutó
    mock_service.set.assert_not_called()


@pytest.mark.asyncio
async def test_cache_service_close():
    """
    🔴 RED: Test que close() cierra la conexión de Redis.

    Given: Un servicio con cliente Redis activo
    When: Se llama a close()
    Then: Debe cerrar la conexión
    """
    from app.services.cache_service import CacheService

    # Arrange
    service = CacheService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    service.client = mock_client

    # Act
    await service.close()

    # Assert
    mock_client.close.assert_called_once()

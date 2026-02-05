"""
Integration test para CacheService con Redis real.

Este test verifica que podemos conectarnos a Redis y realizar operaciones reales.
Requiere que Redis esté corriendo en Docker.
"""

import pytest

from app.core.config import settings
from app.services.cache_service import CacheService, cached


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cache_service_integration_with_redis():
    """
    Test de integración: conectar a Redis real y realizar operaciones.

    Given: Redis corriendo en Docker
    When: Creamos CacheService y realizamos operaciones
    Then: Las operaciones deben ejecutarse exitosamente
    """
    # Arrange
    service = CacheService(redis_url=settings.REDIS_URL)

    try:
        # Test SET y GET
        key = "test:integration:key"
        value = "test_value_123"

        # Act - Set
        result = await service.set(key, value, ttl=60)
        assert result is True

        # Act - Get
        retrieved_value = await service.get(key)
        assert retrieved_value == value

        # Act - Exists
        exists = await service.exists(key)
        assert exists is True

        # Act - Delete
        deleted = await service.delete(key)
        assert deleted is True

        # Verify deletion
        exists_after = await service.exists(key)
        assert exists_after is False

        # Get non-existent key
        retrieved_after = await service.get(key)
        assert retrieved_after is None

    finally:
        # Cleanup
        await service.delete("test:integration:key")
        await service.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cached_decorator_integration():
    """
    Test de integración: verificar que @cached funciona con Redis real.

    Given: Redis corriendo y una función decorada
    When: Llamamos la función múltiples veces
    Then: El resultado debe cachearse correctamente
    """
    # Arrange
    service = CacheService(redis_url=settings.REDIS_URL)
    call_count = 0

    @cached(ttl=30, cache_service=service, key_prefix="test:")
    async def expensive_operation(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    try:
        # Limpiar TODO el cache de Redis para evitar contaminación entre tests
        await service.client.flushdb()

        # Primera llamada - ejecuta función
        result1 = await expensive_operation(10)
        assert result1 == 20
        assert call_count == 1

        # Segunda llamada - debe retornar del cache como STRING
        result2 = await expensive_operation(10)
        assert result2 == "20"  # String porque viene del cache
        assert call_count == 1  # No incrementa, usó cache

        # Llamada con argumento diferente - ejecuta función
        result3 = await expensive_operation(5)
        assert result3 == 10
        assert call_count == 2

    finally:
        # Cleanup
        await service.client.flushdb()
        await service.close()

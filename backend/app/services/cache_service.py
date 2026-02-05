"""
Cache Service - Cliente para Redis.

Servicio para gestionar caché usando Redis con soporte asíncrono.
Incluye manejo de errores robusto para no fallar la aplicación si Redis no está disponible.
"""

import hashlib
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis.asyncio as aioredis


logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio para gestionar caché con Redis.

    Proporciona métodos para get, set, delete y exists con manejo de errores robusto.
    Si Redis falla, loggea warnings pero no hace crash de la aplicación.
    """

    def __init__(self, redis_url: str):
        """
        Inicializa el cliente de Redis.

        Args:
            redis_url: URL de conexión a Redis (ej: redis://localhost:6379/0)

        Example:
            >>> service = CacheService(redis_url="redis://localhost:6379/0")
        """
        self.redis_url = redis_url
        self.client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=False)

    async def get(self, key: str) -> str | None:
        """
        Obtiene un valor del caché por su clave.

        Args:
            key: Clave a buscar en el caché

        Returns:
            Optional[str]: Valor almacenado o None si no existe o hay error

        Example:
            >>> value = await cache_service.get("user:123")
            >>> if value:
            ...     print(f"Cached value: {value}")
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            # Decode bytes to string
            if isinstance(value, bytes):
                return value.decode("utf-8")
            return value
        except Exception as e:
            logger.warning(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """
        Almacena un valor en el caché con TTL.

        Args:
            key: Clave para almacenar
            value: Valor a almacenar (será convertido a string)
            ttl: Tiempo de vida en segundos (default: 300 = 5 minutos)

        Returns:
            bool: True si se almacenó exitosamente, False si hubo error

        Example:
            >>> await cache_service.set("user:123", "John Doe", ttl=600)
        """
        try:
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Elimina una clave del caché.

        Args:
            key: Clave a eliminar

        Returns:
            bool: True si se eliminó, False si no existe o hubo error

        Example:
            >>> await cache_service.delete("user:123")
        """
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis DELETE error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en el caché.

        Args:
            key: Clave a verificar

        Returns:
            bool: True si existe, False si no existe o hay error

        Example:
            >>> if await cache_service.exists("user:123"):
            ...     print("Key exists in cache")
        """
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def close(self) -> None:
        """
        Cierra la conexión a Redis.

        Example:
            >>> await cache_service.close()
        """
        try:
            await self.client.close()
        except Exception as e:
            logger.warning(f"Redis CLOSE error: {e}")


def cached(
    ttl: int = 300, cache_service: CacheService | None = None, key_prefix: str = ""
) -> Callable:
    """
    Decorator para cachear resultados de funciones asíncronas.

    El decorator genera una clave única basada en el nombre de la función
    y sus argumentos, y cachea el resultado por el TTL especificado.

    Args:
        ttl: Tiempo de vida del caché en segundos (default: 300)
        cache_service: Instancia de CacheService a usar (opcional)
        key_prefix: Prefijo opcional para las claves de caché

    Returns:
        Callable: Función decorada con caché

    Example:
        >>> @cached(ttl=600)
        >>> async def get_user(user_id: int):
        ...     return await database.fetch_user(user_id)
        >>>
        >>> # Primera llamada: ejecuta la función y cachea
        >>> user = await get_user(123)
        >>> # Segunda llamada: retorna del caché
        >>> user = await get_user(123)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Si no hay cache_service, ejecutar función sin caché
            if cache_service is None:
                return await func(*args, **kwargs)

            # Generar clave única basada en función y argumentos
            func_name = func.__name__
            args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()
            cache_key = f"{key_prefix}{func_name}:{args_hash}"

            # Intentar obtener del caché
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT for {cache_key}")
                return cached_value

            # Cache miss: ejecutar función
            logger.debug(f"Cache MISS for {cache_key}")
            result = await func(*args, **kwargs)

            # Almacenar resultado en caché (convertir a string si es necesario)
            if result is not None:
                cache_value = result if isinstance(result, str) else str(result)
                await cache_service.set(cache_key, cache_value, ttl=ttl)

            return result

        return wrapper

    return decorator

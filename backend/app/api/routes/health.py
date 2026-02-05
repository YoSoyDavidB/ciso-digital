"""
Health Check Endpoints.

Endpoints para verificar el estado de la aplicación y sus dependencias.
"""

import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import get_async_engine
from app.services.cache_service import CacheService
from app.services.vector_store import VectorStoreService


logger = logging.getLogger(__name__)

# =============================================================================
# Schemas
# =============================================================================


class HealthResponse(BaseModel):
    """Response del health check con información de servicios."""

    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        ..., description="Estado general de la aplicación"
    )
    timestamp: str = Field(..., description="Timestamp ISO UTC del check")
    services: dict[str, str] = Field(..., description="Estado de cada servicio")
    version: str = Field(..., description="Versión de la API")
    environment: str = Field(..., description="Entorno de ejecución")


class ReadinessResponse(BaseModel):
    """Response del readiness check."""

    ready: bool = Field(..., description="Indica si el sistema está listo")
    timestamp: str = Field(..., description="Timestamp ISO UTC del check")


# =============================================================================
# Router
# =============================================================================

router = APIRouter(tags=["Health"])


# =============================================================================
# Helper Functions
# =============================================================================


async def check_database_health() -> bool:
    """
    Verifica la salud de la base de datos PostgreSQL.

    Returns:
        bool: True si la DB responde correctamente, False si hay error
    """
    try:
        from sqlalchemy import text

        engine = get_async_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


async def check_redis_health() -> bool:
    """
    Verifica la salud del cache Redis.

    Returns:
        bool: True si Redis responde correctamente, False si hay error
    """
    try:
        service = CacheService(redis_url=settings.REDIS_URL)
        await service.set("health_check", "ok", ttl=10)
        result = await service.get("health_check")
        await service.delete("health_check")
        await service.close()
        return result == "ok"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


async def check_qdrant_health() -> bool:
    """
    Verifica la salud de Qdrant vector database.

    Returns:
        bool: True si Qdrant responde correctamente, False si hay error
    """
    try:
        service = VectorStoreService(
            qdrant_url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )
        # Try to list collections as a simple health check
        await service.client.get_collections()
        return True
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        return False


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check completo",
    description="Verifica el estado de la aplicación y todos sus servicios.",
)
async def health_check(response: Response) -> HealthResponse:
    """
    Health check completo con verificación de servicios.

    Verifica el estado de:
    - Base de datos (PostgreSQL)
    - Cache (Redis)
    - Vector DB (Qdrant)

    Returns:
        HealthResponse: Estado de todos los servicios

    Status Codes:
        - 200: Sistema healthy o degraded (servicios no críticos caídos)
        - 503: Sistema unhealthy (servicios críticos caídos)
    """
    # Check all services
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()
    qdrant_healthy = await check_qdrant_health()

    # Build services status dict
    services = {
        "database": "healthy" if db_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
        "qdrant": "healthy" if qdrant_healthy else "unhealthy",
    }

    # Determine overall status
    # Database is critical - if down, system is unhealthy
    # Redis and Qdrant are important but not critical - degraded if down
    if not db_healthy:
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not redis_healthy or not qdrant_healthy:
        overall_status = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        overall_status = "healthy"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        services=services,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Verifica si el sistema está listo para recibir tráfico.",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """
    Readiness check para Kubernetes/orchestrators.

    Verifica solo servicios críticos (database) para determinar
    si el sistema puede recibir requests.

    Returns:
        ReadinessResponse: Indica si el sistema está listo

    Status Codes:
        - 200: Sistema listo
        - 503: Sistema no listo
    """
    # Only check critical services for readiness
    db_healthy = await check_database_health()

    if not db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        ready = False
    else:
        ready = True

    return ReadinessResponse(
        ready=ready,
        timestamp=datetime.utcnow().isoformat(),
    )

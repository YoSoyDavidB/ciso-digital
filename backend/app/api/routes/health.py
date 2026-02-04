"""
Health Check Endpoints.

Endpoints para verificar el estado de la aplicación y sus dependencias.
"""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field


# =============================================================================
# Schemas
# =============================================================================


class HealthResponse(BaseModel):
    """Response del health check básico."""

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Estado general de la aplicación"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp UTC del check"
    )


class ServiceStatus(BaseModel):
    """Estado de un servicio individual."""

    name: str = Field(..., description="Nombre del servicio")
    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        ..., description="Estado del servicio"
    )
    message: str | None = Field(default=None, description="Mensaje adicional o error")
    response_time_ms: float | None = Field(default=None, description="Tiempo de respuesta en ms")


class DetailedHealthResponse(BaseModel):
    """Response del health check detallado."""

    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        ..., description="Estado general agregado"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp UTC del check"
    )
    services: dict[str, ServiceStatus] = Field(..., description="Estado de servicios individuales")
    version: str = Field(default="0.1.0", description="Versión de la API")


# =============================================================================
# Router
# =============================================================================

router = APIRouter(prefix="/health", tags=["Health"])


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check básico",
    description="Endpoint simple para verificar que la API está corriendo.",
)
async def health_check() -> HealthResponse:
    """
    Health check básico.

    Retorna un status simple indicando que la aplicación está activa.
    Útil para load balancers y orquestadores (Kubernetes, Docker Swarm).

    Returns:
        HealthResponse: Status healthy con timestamp
    """
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())


@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check detallado",
    description="Verificación detallada del estado de todos los servicios.",
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Health check detallado.

    Verifica el estado de todos los servicios críticos:
    - Base de datos (PostgreSQL)
    - Cache (Redis)
    - Vector DB (Qdrant)

    Returns:
        DetailedHealthResponse: Estado detallado de todos los servicios

    Note:
        Por ahora retorna valores mock. En fases futuras se implementarán
        checks reales contra las dependencias.
    """
    # TODO: Implementar checks reales cuando los servicios estén disponibles
    services = {
        "database": ServiceStatus(
            name="PostgreSQL",
            status="healthy",
            message="Mock - Database check not implemented yet",
            response_time_ms=1.5,
        ),
        "cache": ServiceStatus(
            name="Redis",
            status="healthy",
            message="Mock - Redis check not implemented yet",
            response_time_ms=0.8,
        ),
        "vector_db": ServiceStatus(
            name="Qdrant",
            status="healthy",
            message="Mock - Qdrant check not implemented yet",
            response_time_ms=2.1,
        ),
    }

    # Determinar status general
    # Si algún servicio está unhealthy → unhealthy
    # Si algún servicio está degraded → degraded
    # Si todos están healthy → healthy
    overall_status: Literal["healthy", "unhealthy", "degraded"] = "healthy"

    for service in services.values():
        if service.status == "unhealthy":
            overall_status = "unhealthy"
            break
        elif service.status == "degraded" and overall_status == "healthy":
            overall_status = "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services,
        version="0.1.0",
    )

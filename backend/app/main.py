"""
CISO Digital API - FastAPI Application.

Aplicación principal FastAPI con configuración de middleware,
logging estructurado y routers.
"""

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings


# =============================================================================
# Logging Configuration
# =============================================================================


def configure_logging() -> None:
    """
    Configura logging estructurado para la aplicación.

    Configuración básica de logging con formato consistente.
    En producción se recomienda usar structlog para logs estructurados.
    """
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    # Configurar formato de logs
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


# Configurar logging al iniciar
configure_logging()
logger = logging.getLogger(__name__)


# =============================================================================
# Lifespan Events
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager para startup y shutdown.

    Maneja eventos de inicio y finalización de la aplicación.
    """
    # Startup
    logger.info("🚀 Starting CISO Digital API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")

    # TODO: Inicializar conexiones a base de datos, Redis, Qdrant
    # await database.connect()
    # await redis_client.connect()
    # await qdrant_client.connect()

    logger.info("✅ Application startup complete")

    yield

    # Shutdown
    logger.info("🛑 Shutting down CISO Digital API...")

    # TODO: Cerrar conexiones
    # await database.disconnect()
    # await redis_client.disconnect()
    # await qdrant_client.disconnect()

    logger.info("✅ Application shutdown complete")


# =============================================================================
# FastAPI App
# =============================================================================


def create_app() -> FastAPI:
    """
    Factory para crear y configurar la aplicación FastAPI.

    Returns:
        FastAPI: Aplicación configurada
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "API REST para CISO Digital - Sistema de operaciones de seguridad "
            "potenciado por IA para gestión proactiva de riesgos, incidentes y "
            "cumplimiento."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # =========================================================================
    # Middleware Configuration
    # =========================================================================

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TODO: Agregar middleware adicional
    # - Rate limiting
    # - Request ID tracking
    # - Authentication
    # - Error handling

    # =========================================================================
    # Router Registration
    # =========================================================================

    # Import routers
    from app.api.routes.health import router as health_router

    # Register routers
    app.include_router(health_router)

    # TODO: Agregar routers adicionales
    # app.include_router(auth_router, prefix="/api/v1")
    # app.include_router(users_router, prefix="/api/v1")
    # app.include_router(chat_router, prefix="/api/v1")
    # app.include_router(risks_router, prefix="/api/v1")
    # app.include_router(incidents_router, prefix="/api/v1")

    # =========================================================================
    # Exception Handlers
    # =========================================================================

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handler global para excepciones no capturadas."""
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
            },
        )

    # =========================================================================
    # Root Endpoint
    # =========================================================================

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, Any]:
        """
        Root endpoint con información de la API.

        Returns información básica y enlaces a documentación.
        """
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }

    return app


# =============================================================================
# App Instance
# =============================================================================

# Crear instancia de la aplicación
app = create_app()


# =============================================================================
# Entry Point (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
# Test error

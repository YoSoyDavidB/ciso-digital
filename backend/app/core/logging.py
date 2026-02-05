"""
Structured Logging Configuration
================================

Configura logging estructurado usando structlog para toda la aplicación.

Features:
- JSON logging en producción para fácil parsing
- Pretty console logging en desarrollo para debugging
- Context binding automático
- Timestamp en todos los logs
- Exception tracking con stack traces

Usage:
    # En app/main.py (startup)
    from app.core.logging import configure_logging
    configure_logging(environment="production", log_level="INFO")

    # En cualquier módulo
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("event_name", user_id="123", action="created_resource")
"""

import logging
import sys
from typing import Literal

import structlog
from structlog.typing import EventDict, Processor


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Procesador custom que agrega contexto de aplicación.

    Args:
        logger: Logger instance
        method_name: Método de logging (info, warning, etc)
        event_dict: Diccionario con datos del evento

    Returns:
        EventDict con contexto adicional
    """
    event_dict["app"] = "ciso-digital"
    event_dict["level"] = method_name
    return event_dict


def configure_logging(
    environment: Literal["development", "production"] = "development",
    log_level: str = "INFO",
) -> None:
    """
    Configura structured logging para la aplicación.

    Args:
        environment: Entorno de ejecución (development/production)
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

    Example:
        >>> configure_logging(environment="production", log_level="INFO")
        >>> logger = get_logger("my_module")
        >>> logger.info("user_logged_in", user_id="123")
    """
    # Set standard library logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    # Add environment-specific renderer
    if environment == "production":
        # JSON for production (machine-readable)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console for development (human-readable)
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=structlog.dev.better_traceback
            )
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Obtiene un logger estructurado con el nombre especificado.

    Args:
        name: Nombre del logger (típicamente __name__ del módulo)

    Returns:
        BoundLogger configurado con structlog

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("operation_completed", duration_ms=150)
    """
    return structlog.get_logger(name)


def log_llm_call(
    agent_name: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    success: bool,
) -> None:
    """
    Loggea una llamada al LLM con métricas.

    Args:
        agent_name: Nombre del agent que hizo la llamada
        model: Modelo usado (ej: claude-sonnet-4.5)
        prompt_tokens: Tokens en el prompt
        completion_tokens: Tokens en la respuesta
        latency_ms: Latencia en milisegundos
        success: Si la llamada fue exitosa
    """
    logger = get_logger("llm")
    logger.info(
        "llm_call_completed",
        agent_name=agent_name,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        latency_ms=latency_ms,
        success=success,
    )


def log_rag_retrieval(
    query: str,
    num_results: int,
    latency_ms: int,
) -> None:
    """
    Loggea una búsqueda en RAG.

    Args:
        query: Query ejecutada
        num_results: Número de documentos retornados
        latency_ms: Latencia en milisegundos
    """
    logger = get_logger("rag")
    logger.info(
        "rag_retrieval_completed",
        query=query,
        num_results=num_results,
        latency_ms=latency_ms,
    )


def log_cache_operation(
    operation: str,
    key: str,
    hit: bool,
    latency_ms: int,
) -> None:
    """
    Loggea una operación de cache.

    Args:
        operation: Tipo de operación (get, set, delete)
        key: Key del cache
        hit: Si fue cache hit (para operación get)
        latency_ms: Latencia en milisegundos
    """
    logger = get_logger("cache")
    logger.info(
        "cache_operation",
        operation=operation,
        key=key,
        hit=hit,
        latency_ms=latency_ms,
    )

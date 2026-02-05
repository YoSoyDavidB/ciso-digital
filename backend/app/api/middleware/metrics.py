"""
Metrics Middleware
==================

Middleware para trackear métricas de la aplicación usando Prometheus.

Métricas incluidas:
- HTTP request count por endpoint y status code
- HTTP request latency (histograma)
- LLM token usage (prompt y completion)
- LLM latency
- Cache hit/miss rate
- RAG retrieval counts

Usage:
    from app.api.middleware.metrics import MetricsMiddleware
    app.add_middleware(MetricsMiddleware)

    # Para exportar métricas
    from app.api.middleware.metrics import get_metrics
    metrics_text = get_metrics()
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    registry=REGISTRY,
)

# ============================================================================
# LLM Metrics
# ============================================================================

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total LLM tokens used",
    ["agent", "model", "token_type"],  # token_type: prompt | completion
    registry=REGISTRY,
)

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["agent", "model", "status"],  # status: success | error
    registry=REGISTRY,
)

llm_request_duration_seconds = Histogram(
    "llm_request_duration_seconds",
    "LLM request latency",
    ["agent", "model"],
    registry=REGISTRY,
)

# ============================================================================
# Cache Metrics
# ============================================================================

cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "result"],  # operation: get|set|delete, result: hit|miss|success
    registry=REGISTRY,
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Cache hit rate (0.0-1.0)",
    registry=REGISTRY,
)

# ============================================================================
# RAG Metrics
# ============================================================================

rag_retrievals_total = Counter(
    "rag_retrievals_total",
    "Total RAG document retrievals",
    registry=REGISTRY,
)

rag_documents_retrieved = Histogram(
    "rag_documents_retrieved",
    "Number of documents retrieved per RAG query",
    registry=REGISTRY,
)

rag_retrieval_duration_seconds = Histogram(
    "rag_retrieval_duration_seconds",
    "RAG retrieval latency",
    registry=REGISTRY,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para trackear métricas HTTP.

    Trackea automáticamente:
    - Request count por endpoint
    - Request latency
    - Status codes
    """

    def __init__(
        self,
        app: ASGIApp,
        registry: CollectorRegistry | None = None,
    ):
        super().__init__(app)
        self.registry = registry or REGISTRY

        # Re-create metrics with custom registry if provided
        if registry and registry != REGISTRY:
            self.http_requests_total = Counter(
                "http_requests_total",
                "Total HTTP requests",
                ["method", "endpoint", "status"],
                registry=registry,
            )
            self.http_request_duration_seconds = Histogram(
                "http_request_duration_seconds",
                "HTTP request latency",
                ["method", "endpoint"],
                registry=registry,
            )
        else:
            self.http_requests_total = http_requests_total
            self.http_request_duration_seconds = http_request_duration_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track metrics.

        Args:
            request: FastAPI Request
            call_next: Next middleware/endpoint handler

        Returns:
            Response with metrics tracked
        """
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Track errors
            status_code = 500
            raise e
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Track metrics
            self.http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code,
            ).inc()

            self.http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path,
            ).observe(duration)

        return response


# ============================================================================
# Helper Functions
# ============================================================================


def track_llm_tokens(
    agent_name: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    registry: CollectorRegistry | None = None,
) -> None:
    """
    Track LLM token usage.

    Args:
        agent_name: Name of the agent making the call
        model: LLM model used
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        registry: Custom registry for testing
    """
    if registry and registry != REGISTRY:
        # Create temporary counter for custom registry
        counter = Counter(
            "llm_tokens_total",
            "Total LLM tokens used",
            ["agent", "model", "token_type"],
            registry=registry,
        )
    else:
        counter = llm_tokens_total

    counter.labels(
        agent=agent_name,
        model=model,
        token_type="prompt",
    ).inc(prompt_tokens)

    counter.labels(
        agent=agent_name,
        model=model,
        token_type="completion",
    ).inc(completion_tokens)


def track_llm_latency(
    agent_name: str,
    model: str,
    latency_seconds: float,
    registry: CollectorRegistry | None = None,
) -> None:
    """
    Track LLM request latency.

    Args:
        agent_name: Name of the agent
        model: LLM model used
        latency_seconds: Request duration in seconds
        registry: Custom registry for testing
    """
    if registry and registry != REGISTRY:
        histogram = Histogram(
            "llm_request_duration_seconds",
            "LLM request latency",
            ["agent", "model"],
            registry=registry,
        )
    else:
        histogram = llm_request_duration_seconds

    histogram.labels(agent=agent_name, model=model).observe(latency_seconds)


def track_cache_operation(
    operation: str,
    hit: bool,
    registry: CollectorRegistry | None = None,
) -> None:
    """
    Track cache operation.

    Args:
        operation: Operation type (get, set, delete)
        hit: Whether it was a cache hit (for get operations)
        registry: Custom registry for testing
    """
    if registry and registry != REGISTRY:
        counter = Counter(
            "cache_operations_total",
            "Total cache operations",
            ["operation", "result"],
            registry=registry,
        )
    else:
        counter = cache_operations_total

    result = "hit" if hit else "miss" if operation == "get" else "success"
    counter.labels(operation=operation, result=result).inc()


def track_rag_retrieval(
    num_documents: int,
    latency_seconds: float,
    registry: CollectorRegistry | None = None,
) -> None:
    """
    Track RAG document retrieval.

    Args:
        num_documents: Number of documents retrieved
        latency_seconds: Retrieval duration in seconds
        registry: Custom registry for testing
    """
    if registry and registry != REGISTRY:
        counter = Counter(
            "rag_retrievals_total",
            "Total RAG document retrievals",
            registry=registry,
        )
        docs_hist = Histogram(
            "rag_documents_retrieved",
            "Number of documents retrieved per RAG query",
            registry=registry,
        )
        latency_hist = Histogram(
            "rag_retrieval_duration_seconds",
            "RAG retrieval latency",
            registry=registry,
        )
    else:
        counter = rag_retrievals_total
        docs_hist = rag_documents_retrieved
        latency_hist = rag_retrieval_duration_seconds

    counter.inc()
    docs_hist.observe(num_documents)
    latency_hist.observe(latency_seconds)


def get_metrics() -> bytes:
    """
    Get current metrics in Prometheus format.

    Returns:
        Metrics as bytes for HTTP response
    """
    return generate_latest(REGISTRY)

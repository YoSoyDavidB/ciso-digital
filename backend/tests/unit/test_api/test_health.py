"""
Tests unitarios para los endpoints de health check.

Los health checks permiten verificar el estado del sistema y sus dependencias.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI."""
    return TestClient(app)


def test_health_endpoint_returns_200_when_all_services_healthy(client):
    """
    Test que /health retorna 200 cuando todos los servicios están saludables.

    Given: Todos los servicios (DB, Redis, Qdrant) están funcionando
    When: Se hace GET a /health
    Then: Debe retornar 200 con status "healthy"
    """
    # Arrange - Mock all health checks to return True
    with (
        patch(
            "app.api.routes.health.check_database_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_redis_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_qdrant_health", new_callable=AsyncMock, return_value=True
        ),
    ):
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert data["services"]["database"] == "healthy"
        assert data["services"]["redis"] == "healthy"
        assert data["services"]["qdrant"] == "healthy"


def test_health_endpoint_returns_503_when_database_unhealthy(client):
    """
    Test que /health retorna 503 cuando la base de datos falla.

    Given: La base de datos no responde
    When: Se hace GET a /health
    Then: Debe retornar 503 con status "unhealthy"
    """
    # Arrange - Simular fallo de DB
    with (
        patch(
            "app.api.routes.health.check_database_health",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch(
            "app.api.routes.health.check_redis_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_qdrant_health", new_callable=AsyncMock, return_value=True
        ),
    ):
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["database"] == "unhealthy"


def test_health_endpoint_returns_503_when_redis_unhealthy(client):
    """
    Test que /health retorna 503 cuando Redis falla.

    Given: Redis no responde
    When: Se hace GET a /health
    Then: Debe retornar 503 con status "degraded"
    """
    # Arrange - Simular fallo de Redis
    with (
        patch(
            "app.api.routes.health.check_database_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_redis_health", new_callable=AsyncMock, return_value=False
        ),
        patch(
            "app.api.routes.health.check_qdrant_health", new_callable=AsyncMock, return_value=True
        ),
    ):
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["redis"] == "unhealthy"


def test_ready_endpoint_returns_200_when_system_ready(client):
    """
    Test que /ready retorna 200 cuando el sistema está listo.

    Given: Todos los servicios críticos están funcionando
    When: Se hace GET a /ready
    Then: Debe retornar 200
    """
    # Arrange - Mock DB health check to return True
    with patch(
        "app.api.routes.health.check_database_health", new_callable=AsyncMock, return_value=True
    ):
        # Act
        response = client.get("/ready")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "timestamp" in data


def test_ready_endpoint_returns_503_when_database_not_ready(client):
    """
    Test que /ready retorna 503 cuando la DB no está lista.

    Given: La base de datos no responde
    When: Se hace GET a /ready
    Then: Debe retornar 503
    """
    # Arrange
    with patch(
        "app.api.routes.health.check_database_health", new_callable=AsyncMock, return_value=False
    ):
        # Act
        response = client.get("/ready")

        # Assert
        assert response.status_code == 503
        data = response.json()
        assert data["ready"] is False


def test_health_endpoint_includes_version_info(client):
    """
    Test que /health incluye información de versión.

    Given: Sistema configurado con versión
    When: Se hace GET a /health
    Then: Debe incluir versión en la respuesta
    """
    # Arrange - Mock all health checks
    with (
        patch(
            "app.api.routes.health.check_database_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_redis_health", new_callable=AsyncMock, return_value=True
        ),
        patch(
            "app.api.routes.health.check_qdrant_health", new_callable=AsyncMock, return_value=True
        ),
    ):
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "environment" in data

"""
Pytest configuration and shared fixtures.

Este archivo contiene fixtures compartidos para todos los tests del proyecto.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


# Importaciones que se habilitarán cuando existan los módulos
# from app.main import app
# from app.database import Base, get_db


# =============================================================================
# Configuración de Asyncio
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Crea un event loop para toda la sesión de tests.

    Esto es necesario para que los fixtures con scope="session"
    funcionen correctamente con pytest-asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

# URL para base de datos en memoria (tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """
    Crea un engine de base de datos para tests.

    Usa SQLite en memoria para tests rápidos y aislados.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Cuando tengamos modelos, crear las tablas:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión de base de datos para cada test.

    Cada test obtiene una sesión limpia que se hace rollback al final.
    """
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


# =============================================================================
# FastAPI Client Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP asíncrono para tests de API.

    Configura el cliente con la app de FastAPI y overrides
    para usar la base de datos de tests.

    Uso:
        async def test_endpoint(async_client):
            response = await async_client.get("/api/v1/health")
            assert response.status_code == 200
    """
    # Importación diferida - se habilitará cuando exista app.main
    # from app.main import app
    # from app.database import get_db

    # Override de dependencia de DB
    # async def override_get_db():
    #     yield db_session

    # app.dependency_overrides[get_db] = override_get_db

    # Por ahora, placeholder hasta que tengamos la app
    # async with AsyncClient(
    #     transport=ASGITransport(app=app),
    #     base_url="http://test"
    # ) as client:
    #     yield client

    # app.dependency_overrides.clear()

    # Placeholder - se reemplazará cuando exista la app
    yield None  # type: ignore


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_settings():
    """
    Configuración mock para tests.

    Proporciona settings de test que no dependen de variables de entorno.
    """
    return {
        "DATABASE_URL": TEST_DATABASE_URL,
        "SECRET_KEY": "test-secret-key-do-not-use-in-production",
        "DEBUG": True,
        "ENVIRONMENT": "test",
    }


# =============================================================================
# Helper Fixtures
# =============================================================================


@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para crear usuarios en tests."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_risk_data():
    """Datos de ejemplo para crear riesgos en tests."""
    return {
        "title": "Test Risk",
        "description": "A test risk for unit testing",
        "severity": "high",
        "likelihood": "medium",
        "impact": "high",
        "status": "identified",
    }

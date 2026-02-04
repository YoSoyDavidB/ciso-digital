"""
Tests para el módulo de configuración.

🔴 RED: Estos tests deben fallar inicialmente porque config.py no existe.
"""

from unittest.mock import patch

import pytest


class TestSettings:
    """Tests para la clase Settings."""

    @pytest.mark.unit
    def test_settings_loads_from_environment(self) -> None:
        """
        Test que Settings carga variables de entorno correctamente.

        Given: Variables de entorno configuradas
        When: Se instancia Settings
        Then: Los valores deben cargarse correctamente
        """
        env_vars = {
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
            "REDIS_URL": "redis://localhost:6379/0",
            "QDRANT_URL": "http://localhost:6333",
            "ANTHROPIC_API_KEY": "sk-ant-test-key",
            "SECRET_KEY": "test-secret-key-min-32-characters-long",
            "ENVIRONMENT": "testing",
        }

        with patch.dict("os.environ", env_vars, clear=False):
            # Import dentro del context para que use las env vars mockeadas
            from app.core.config import Settings

            settings = Settings()

            assert env_vars["DATABASE_URL"] == settings.DATABASE_URL
            assert env_vars["REDIS_URL"] == settings.REDIS_URL
            assert env_vars["QDRANT_URL"] == settings.QDRANT_URL
            assert env_vars["ANTHROPIC_API_KEY"] == settings.ANTHROPIC_API_KEY
            assert env_vars["SECRET_KEY"] == settings.SECRET_KEY
            assert settings.ENVIRONMENT == "testing"

    @pytest.mark.unit
    def test_settings_has_default_values(self) -> None:
        """
        Test que Settings tiene valores por defecto apropiados.

        Given: Variables de entorno mínimas con DEBUG explícito
        When: Se instancia Settings
        Then: Los valores por defecto deben estar configurados
        """
        env_vars = {
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
            "SECRET_KEY": "test-secret-key-min-32-characters-long",
            "DEBUG": "false",  # Explicit to override any .env file
        }

        with patch.dict("os.environ", env_vars, clear=False):
            from app.core.config import Settings

            settings = Settings()

            # Valores por defecto
            assert settings.ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.DEBUG is False
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
            assert settings.LLM_MODEL == "claude-sonnet-4-20250514"

    @pytest.mark.unit
    def test_settings_singleton_pattern(self) -> None:
        """
        Test que get_settings retorna la misma instancia (cached).

        Given: Función get_settings
        When: Se llama múltiples veces
        Then: Debe retornar la misma configuración
        """
        from app.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Deben ser la misma instancia (o al menos equivalentes)
        assert settings1.SECRET_KEY == settings2.SECRET_KEY
        assert settings1.ALGORITHM == settings2.ALGORITHM

    @pytest.mark.unit
    def test_settings_environment_enum(self) -> None:
        """
        Test que ENVIRONMENT acepta valores válidos.

        Given: Valores válidos de environment
        When: Se configura ENVIRONMENT
        Then: Debe aceptar: development, testing, staging, production
        """
        from app.core.config import Settings

        valid_environments = ["development", "testing", "staging", "production"]

        for env in valid_environments:
            env_vars = {
                "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
                "SECRET_KEY": "test-secret-key-min-32-characters-long",
                "ENVIRONMENT": env,
            }

            with patch.dict("os.environ", env_vars, clear=False):
                settings = Settings()
                assert env == settings.ENVIRONMENT

    @pytest.mark.unit
    def test_settings_debug_mode_in_development(self) -> None:
        """
        Test que DEBUG puede habilitarse.

        Given: DEBUG=true en environment
        When: Se instancia Settings
        Then: DEBUG debe ser True
        """
        env_vars = {
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
            "SECRET_KEY": "test-secret-key-min-32-characters-long",
            "DEBUG": "true",
        }

        with patch.dict("os.environ", env_vars, clear=False):
            from app.core.config import Settings

            settings = Settings()
            assert settings.DEBUG is True

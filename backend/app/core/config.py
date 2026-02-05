"""
Application Configuration Module.

Configuración centralizada usando pydantic-settings.
Carga variables de entorno desde .env y proporciona validación.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Carga automáticamente desde variables de entorno y archivo .env.
    Usa validación de Pydantic para asegurar tipos correctos.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    APP_NAME: str = "CISO Digital API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = "development"

    # ==========================================================================
    # Database
    # ==========================================================================
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection URL (asyncpg)",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/ciso_db"],
    )

    # ==========================================================================
    # Redis (Caching)
    # ==========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
    )

    # ==========================================================================
    # Qdrant (Vector DB)
    # ==========================================================================
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="Qdrant vector database URL",
    )
    QDRANT_API_KEY: str | None = Field(
        default=None,
        description="Qdrant API key (optional for local)",
    )

    # ==========================================================================
    # LLM Services
    # ==========================================================================
    ANTHROPIC_API_KEY: str | None = Field(
        default=None,
        description="Anthropic API key for Claude",
    )
    OPENAI_API_KEY: str | None = Field(
        default=None,
        description="OpenAI API key (fallback/embeddings)",
    )
    LLM_MODEL: str = Field(
        default="claude-sonnet-4-20250514",
        description="Default LLM model to use",
    )
    LLM_MAX_TOKENS: int = Field(
        default=4096,
        description="Maximum tokens for LLM responses",
    )

    # ==========================================================================
    # Security / JWT
    # ==========================================================================
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT signing (min 32 chars)",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        description="Access token expiration in minutes",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        description="Refresh token expiration in days",
    )

    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: str | list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # ==========================================================================
    # Logging
    # ==========================================================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ==========================================================================
    # Validators
    # ==========================================================================
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Valida que la URL de base de datos sea válida."""
        if not v.startswith(("postgresql", "sqlite")):
            raise ValueError("DATABASE_URL must be a PostgreSQL or SQLite URL")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parsea CORS_ORIGINS desde string separado por comas."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Retorna la instancia de Settings (cached).

    Usa lru_cache para singleton pattern - la configuración
    se carga una sola vez y se reutiliza.

    Returns:
        Settings: Instancia de configuración
    """
    # pydantic-settings loads required fields from env/.env file
    return Settings()  # type: ignore[call-arg]


# Instancia global para imports directos
# Uso: from app.core.config import settings
settings = get_settings()

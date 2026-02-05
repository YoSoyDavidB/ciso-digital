"""
Database configuration and session management.

This module provides SQLAlchemy async engine, session factory, and
dependency injection for FastAPI endpoints.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.shared.models.base import Base


@lru_cache
def get_async_engine() -> AsyncEngine:
    """
    Get or create the SQLAlchemy async engine (singleton).

    Uses connection pooling with min=5, max=20 connections.

    Returns:
        AsyncEngine: SQLAlchemy async engine instance

    Example:
        >>> engine = get_async_engine()
        >>> async with engine.begin() as conn:
        ...     await conn.execute(text("SELECT 1"))
    """
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=15,  # pool_size + max_overflow = 20 max connections
    )


@lru_cache
def get_async_session_local() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the async session factory (singleton).

    Returns:
        async_sessionmaker: Factory for creating AsyncSession instances

    Example:
        >>> SessionLocal = get_async_session_local()
        >>> async with SessionLocal() as session:
        ...     result = await session.execute(select(Risk))
    """
    engine = get_async_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields an AsyncSession and ensures it's closed after use.

    Yields:
        AsyncSession: Database session for the request

    Example:
        >>> @app.get("/risks")
        >>> async def get_risks(db: AsyncSession = Depends(get_db)):
        ...     result = await db.execute(select(Risk))
        ...     return result.scalars().all()
    """
    SessionLocal = get_async_session_local()
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called on application startup to ensure
    all tables defined in models exist in the database.

    Example:
        >>> await init_db()
        >>> # All tables from Base.metadata are now created

    Note:
        In production, use Alembic migrations instead of this function.
    """
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

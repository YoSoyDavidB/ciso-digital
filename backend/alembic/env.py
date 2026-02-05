"""
Alembic migration environment configuration.

This module configures Alembic to work with async SQLAlchemy and our application models.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import app settings and models
from app.core.config import settings
from app.shared.models import Base  # Import Base metadata

# This is the Alembic Config object, which provides access to the .ini file
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata for 'autogenerate' support
# This allows Alembic to detect model changes automatically
target_metadata = Base.metadata

# Override sqlalchemy.url with our app's DATABASE_URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the
    Engine creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    Use case: Generate SQL scripts for manual execution.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Execute migrations with the given connection.

    Args:
        connection: Active database connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in async mode.

    Creates an async engine and runs migrations within an async context.
    This is the recommended approach for async SQLAlchemy applications.
    """
    # Create async engine from config
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Run migrations in a sync context (Alembic requirement)
        await connection.run_sync(do_run_migrations)

    # Dispose of the engine
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we create an async Engine and associate
    a connection with the context.

    Use case: Normal migration execution (upgrade/downgrade).
    
    Note: SQLite uses synchronous mode, PostgreSQL uses async mode.
    """
    # Get the database URL
    database_url = config.get_main_option("sqlalchemy.url")
    
    # SQLite requires synchronous mode (no async driver in standard library)
    if database_url and database_url.startswith("sqlite"):
        from sqlalchemy import engine_from_config
        
        # Create synchronous engine for SQLite
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        
        with connectable.connect() as connection:
            do_run_migrations(connection)
        
        connectable.dispose()
    else:
        # Use async mode for PostgreSQL and other async databases
        asyncio.run(run_async_migrations())


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

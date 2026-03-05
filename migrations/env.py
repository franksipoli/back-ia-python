"""Alembic environment configuration."""

from __future__ import with_statement

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.orm import declarative_base

from alembic import context

# Import settings directly without async engine
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import settings

# Create Base locally to avoid async engine initialization
Base = declarative_base()

# Import models to register them with Base
try:
    from src.infra.models import User, RefreshToken, EmailVerification, PhoneVerification
    target_metadata = Base.metadata
except Exception:
    # If models can't be imported, use empty metadata
    target_metadata = Base.metadata

# Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations 'offline'.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use synchronous URL for migrations (psycopg2 instead of asyncpg)
    url = settings.database_url
    if "postgresql" in url:
        # Ensure we use synchronous driver
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        if "postgresql:///" not in url and "postgresql://" in url:
            pass  # URL is already correct
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations 'online'.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from sqlalchemy import create_engine
    
    url = settings.database_url
    if "postgresql" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql://")

    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.begin() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


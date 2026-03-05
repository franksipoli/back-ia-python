"""Configuração do banco de dados SQLAlchemy."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

logger = logging.getLogger(__name__)

# Engine assíncrono (será criado lazy para evitar problemas com migrações)
_engine = None


def get_engine():
    """Cria engine assíncrono lazy."""
    global _engine
    if _engine is None:
        # Usa asyncpg como driver assíncrono
        db_url = settings.database_url
        if "postgresql://" in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
        logger.info(f"Criando engine para URL: {db_url[:50]}...")
        
        _engine = create_async_engine(
            db_url,
            echo=settings.python_env == "development",
            future=True,
            pool_pre_ping=True,
        )
    return _engine


# Session factory (lazy)
_async_session = None


def get_async_session_factory():
    """Cria factory de sessões lazy."""
    global _async_session
    if _async_session is None:
        _async_session = sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _async_session


async_session = get_async_session_factory()

# Base para modelos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para injetar sessão do banco em rotas."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

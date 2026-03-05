"""Configuração do pytest."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.infra.database import Base, get_db
from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Cria engine de teste."""
    # Usa banco em memória ou teste
    test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Cria sessão de teste."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session

    session.rollback()


@pytest.fixture
def override_get_db(test_session):
    """Override da dependência get_db para testes."""

    async def _override_get_db():
        yield test_session

    return _override_get_db


@pytest.fixture
def test_client(override_get_db):
    """Cliente de teste do FastAPI."""
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)

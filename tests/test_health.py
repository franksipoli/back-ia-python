"""Testes de health check."""

import pytest

from src.config import settings


@pytest.mark.asyncio
async def test_health_check(test_client):
    """Testa health check endpoint."""
    response = test_client.get(f"/{settings.api_prefix}/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "environment" in data
    assert "version" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Testa root endpoint."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data

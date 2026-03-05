"""Testes de autenticação."""

import pytest
from httpx import AsyncClient

from src.config import settings


@pytest.mark.asyncio
async def test_register_user(test_client):
    """Testa registro de novo usuário."""
    response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(test_client):
    """Testa registro com email duplicado."""
    # Primeiro registro
    response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )
    assert response.status_code == 201

    # Segundo registro com mesmo email
    response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "Maria Silva",
            "email": "joao@example.com",  # Email duplicado
            "cpf_cnpj": "98765432101",
            "celular": "11999999999",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_user(test_client):
    """Testa login de usuário."""
    # Registra usuário
    test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )

    # Realiza login
    response = test_client.post(
        f"/{settings.api_prefix}/auth/login",
        json={"email": "joao@example.com", "password": "BurtyPassword123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client):
    """Testa login com credenciais inválidas."""
    response = test_client.post(
        f"/{settings.api_prefix}/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(test_client):
    """Testa obtenção de dados do usuário autenticado."""
    # Registra e faz login
    register_response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )

    access_token = register_response.json()["access_token"]

    # Busca dados do usuário
    response = test_client.get(
        f"/{settings.api_prefix}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "joao@example.com"
    assert data["user"]["name"] == "João Silva"


@pytest.mark.asyncio
async def test_change_password(test_client):
    """Testa alteração de senha."""
    # Registra usuário
    register_response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "OldPassword123!",
            "password_confirm": "OldPassword123!",
        },
    )

    access_token = register_response.json()["access_token"]

    # Altera senha
    response = test_client.patch(
        f"/{settings.api_prefix}/auth/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!",
        },
    )

    assert response.status_code == 200

    # Tenta login com nova senha
    login_response = test_client.post(
        f"/{settings.api_prefix}/auth/login",
        json={"email": "joao@example.com", "password": "NewPassword123!"},
    )

    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_logout(test_client):
    """Testa logout."""
    # Registra usuário
    register_response = test_client.post(
        f"/{settings.api_prefix}/auth/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf_cnpj": "12345678901",
            "celular": "11987654321",
            "password": "BurtyPassword123!",
            "password_confirm": "BurtyPassword123!",
        },
    )

    refresh_token = register_response.json()["refresh_token"]

    # Realiza logout
    response = test_client.post(
        f"/{settings.api_prefix}/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 204

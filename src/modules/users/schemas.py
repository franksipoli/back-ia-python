"""Schemas (DTOs) para usuários."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserDetailResponse(BaseModel):
    """Response com detalhes do usuário."""

    id: str = Field(..., description="ID do usuário (UUID)")
    name: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    celular: str = Field(..., description="Celular")
    role: str = Field(..., description="Role do usuário (ADMIN ou USER)")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Response com lista de usuários."""

    id: str = Field(..., description="ID do usuário (UUID)")
    name: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    role: str = Field(..., description="Role do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    created_at: datetime = Field(..., description="Data de criação")

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    """Request para criar usuário (ADMIN only)."""

    name: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    email: str = Field(..., description="Email único")
    cpf_cnpj: str = Field(..., description="CPF (11 dígitos) ou CNPJ (14 dígitos)")
    celular: str = Field(..., description="Celular com DDD (11 dígitos)")
    role: str = Field(default="USER", description="Role (ADMIN ou USER)")
    password: str = Field(..., min_length=8, description="Senha inicial (mínimo 8 caracteres)")


class UpdateUserRequest(BaseModel):
    """Request para atualizar usuário (ADMIN only)."""

    is_active: bool = Field(..., description="Ativar/desativar usuário")
    role: str = Field(..., description="Role (ADMIN ou USER)")


class UsersListPaginatedResponse(BaseModel):
    """Response com lista paginada de usuários."""

    data: list[UserListResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

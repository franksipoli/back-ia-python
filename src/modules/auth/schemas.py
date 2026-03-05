"""Schemas (DTOs) para autenticação."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Request para login."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")


class RegisterRequest(BaseModel):
    """Request para registro de novo usuário."""

    name: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    email: EmailStr = Field(..., description="Email único")
    cpf_cnpj: str = Field(..., description="CPF (11 dígitos) ou CNPJ (14 dígitos)")
    celular: str = Field(..., description="Celular com DDD (11 dígitos)")
    password: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")
    password_confirm: str = Field(..., description="Confirmação da senha")

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, value: str) -> str:
        """Valida CPF ou CNPJ."""
        # Remove caracteres especiais
        clean = "".join(filter(str.isdigit, value))

        # CPF tem 11 dígitos, CNPJ tem 14
        if len(clean) not in (11, 14):
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")

        return clean

    @field_validator("celular")
    @classmethod
    def validate_celular(cls, value: str) -> str:
        """Valida celular."""
        clean = "".join(filter(str.isdigit, value))

        if len(clean) != 11:
            raise ValueError("Celular deve ter 11 dígitos (DDD + número)")

        return clean

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, value: str, info):
        """Valida se as senhas coincidem."""
        if info.data.get("password") != value:
            raise ValueError("Senhas não coincidem")
        return value


class TokenResponse(BaseModel):
    """Response com tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token para renovação")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Expiração do access token em segundos")


class UserResponse(BaseModel):
    """Response com dados do usuário."""

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


class AuthMeResponse(BaseModel):
    """Response de GET /auth/me."""

    user: UserResponse = Field(..., description="Dados do usuário autenticado")


class ChangePasswordRequest(BaseModel):
    """Request para alterar senha."""

    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")
    new_password_confirm: str = Field(..., description="Confirmação da nova senha")

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, value: str, info):
        """Valida se as novas senhas coincidem."""
        if info.data.get("new_password") != value:
            raise ValueError("Senhas não coincidem")
        return value


class RefreshTokenRequest(BaseModel):
    """Request para renovar access token."""

    refresh_token: str = Field(..., description="Refresh token válido")


class EmailVerificationRequest(BaseModel):
    """Request para solicitar verificação de email."""

    email: EmailStr = Field(..., description="Email a ser verificado")


class EmailVerificationConfirmRequest(BaseModel):
    """Request para confirmar verificação de email."""

    email: EmailStr = Field(..., description="Email sendo verificado")
    token: str = Field(..., description="Token recebido no email")


class PhoneVerificationRequest(BaseModel):
    """Request para solicitar verificação de telefone."""

    phone: str = Field(..., description="Telefone a ser verificado (11 dígitos)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Valida telefone."""
        clean = "".join(filter(str.isdigit, value))

        if len(clean) != 11:
            raise ValueError("Telefone deve ter 11 dígitos (DDD + número)")

        return clean


class PhoneVerificationConfirmRequest(BaseModel):
    """Request para confirmar verificação de telefone."""

    phone: str = Field(..., description="Telefone sendo verificado")
    token: str = Field(..., description="Token recebido via SMS/Telegram")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Valida telefone."""
        clean = "".join(filter(str.isdigit, value))

        if len(clean) != 11:
            raise ValueError("Telefone deve ter 11 dígitos (DDD + número)")

        return clean

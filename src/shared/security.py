"""Funções de segurança: JWT, hashing e autenticação."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from jwt import DecodeError, ExpiredSignatureError, decode, encode


class HTTPAuthenticationCredentials(BaseModel):
    """Simple credentials model for HTTP authentication."""
    scheme: str
    credentials: str

from src.config import settings
from src.infra.models import User

# Instâncias
password_hasher = PasswordHasher()
security = HTTPBearer()


# ============================================================================
# Hashing de Senhas
# ============================================================================


def hash_password(password: str) -> str:
    """Faz hash da senha usando argon2."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    try:
        password_hasher.verify(password_hash, password)
        return True
    except (InvalidHash, VerifyMismatchError):
        return False


# ============================================================================
# JWT - Access Token
# ============================================================================


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Cria um access token JWT."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_expires_in),
    }
    return encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifica e valida um access token JWT."""
    try:
        payload = decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


# ============================================================================
# JWT - Refresh Token
# ============================================================================


def create_refresh_token(user_id: str) -> str:
    """Cria um refresh token JWT."""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.refresh_token_expires_in),
    }
    return encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_refresh_token(token: str) -> dict:
    """Decodifica e valida um refresh token JWT."""
    try:
        payload = decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )


# ============================================================================
# Hash de Tokens (para armazenar no DB)
# ============================================================================


def hash_token(token: str) -> str:
    """Faz hash de um token para armazenar com segurança no DB."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verifica se um token corresponde ao seu hash."""
    return hash_token(token) == token_hash


# ============================================================================
# Dependências para Rotas Protegidas
# ============================================================================


async def get_current_user(
    credentials: HTTPAuthenticationCredentials = Depends(security),
) -> dict:
    """Extrai e valida o usuário do token JWT."""
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload


async def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Valida se o usuário atual é ADMIN."""
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user

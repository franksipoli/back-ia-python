"""Modelos SQLAlchemy do banco de dados."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.database import Base
import uuid


class RoleEnum(PyEnum):
    """Enum de roles de usuário."""

    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    """Modelo de usuário."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    cpf_cnpj: Mapped[str] = mapped_column(
        String(14),
        unique=True,
        nullable=False,
        index=True,
    )
    celular: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(50),
        default="USER",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        "EmailVerification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    phone_verifications: Mapped[list["PhoneVerification"]] = relationship(
        "PhoneVerification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class RefreshToken(Base):
    """Modelo de refresh token (para revogação e controle de sessão)."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relacionamento
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked_at is not None})>"


class VerificationStatusEnum(PyEnum):
    """Enum de status de verificação."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"


class EmailVerification(Base):
    """Modelo para tokens de verificação de email."""

    __tablename__ = "email_verifications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relacionamento
    user: Mapped["User"] = relationship("User", back_populates="email_verifications")

    def __repr__(self) -> str:
        return f"<EmailVerification(id={self.id}, email={self.email}, status={self.status})>"


class PhoneVerification(Base):
    """Modelo para tokens de verificação de telefone/SMS."""

    __tablename__ = "phone_verifications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relacionamento
    user: Mapped["User"] = relationship("User", back_populates="phone_verifications")

    def __repr__(self) -> str:
        return f"<PhoneVerification(id={self.id}, phone={self.phone}, status={self.status})>"

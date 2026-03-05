"""Serviço de autenticação - lógica de negócio."""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infra.models import EmailVerification, PhoneVerification, RefreshToken, User
from src.shared.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from src.shared.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)


class AuthService:
    """Serviço de autenticação."""

    @staticmethod
    async def register(
        name: str,
        email: str,
        cpf_cnpj: str,
        celular: str,
        password: str,
        db: AsyncSession,
    ) -> User:
        """Registra novo usuário."""
        # Verifica se email já existe
        existing_email = await db.execute(select(User).where(User.email == email))
        if existing_email.scalar_one_or_none():
            raise ConflictError("Email já foi registrado")

        # Verifica se CPF/CNPJ já existe
        existing_cpf = await db.execute(select(User).where(User.cpf_cnpj == cpf_cnpj))
        if existing_cpf.scalar_one_or_none():
            raise ConflictError("CPF/CNPJ já foi registrado")

        # Verifica se celular já existe
        existing_phone = await db.execute(select(User).where(User.celular == celular))
        if existing_phone.scalar_one_or_none():
            raise ConflictError("Celular já foi registrado")

        # Cria novo usuário
        user = User(
            name=name,
            email=email,
            cpf_cnpj=cpf_cnpj,
            celular=celular,
            password_hash=hash_password(password),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def login(email: str, password: str, db: AsyncSession) -> tuple[str, str]:
        """Realiza login e retorna (access_token, refresh_token)."""
        # Busca usuário por email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Email ou senha inválidos")

        if not user.is_active:
            raise UnauthorizedError("Usuário inativo")

        # Cria tokens
        access_token = create_access_token(str(user.id), user.email, user.role)
        refresh_token = create_refresh_token(str(user.id))

        # Armazena refresh token no banco (com hash)
        token_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.refresh_token_expires_in
        )

        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(refresh_token_obj)
        await db.commit()

        return access_token, refresh_token

    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> str:
        """Renova access token usando refresh token válido."""
        # Decodifica e valida refresh token (validação JWT)
        from src.shared.security import decode_refresh_token

        payload = decode_refresh_token(refresh_token)
        token_hash = hash_token(refresh_token)

        # Busca refresh token no banco
        result = await db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked_at.is_(None),
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            raise UnauthorizedError("Refresh token inválido ou expirado")

        # Busca usuário
        result = await db.execute(select(User).where(User.id == stored_token.user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("Usuário inativo")

        # Cria novo access token
        access_token = create_access_token(str(user.id), user.email, user.role)

        return access_token

    @staticmethod
    async def logout(refresh_token: str, db: AsyncSession) -> None:
        """Revoga refresh token (logout)."""
        token_hash = hash_token(refresh_token)

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token_obj = result.scalar_one_or_none()

        if not token_obj:
            raise NotFoundError("Token não encontrado")

        token_obj.revoked_at = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
        """Busca usuário por ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("Usuário não encontrado")

        return user

    @staticmethod
    async def change_password(
        user_id: str,
        current_password: str,
        new_password: str,
        db: AsyncSession,
    ) -> None:
        """Altera a senha do usuário."""
        user = await AuthService.get_user_by_id(user_id, db)

        # Valida senha atual
        if not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Senha atual inválida")

        # Atualiza senha
        user.password_hash = hash_password(new_password)
        await db.commit()

    @staticmethod
    async def request_email_verification(
        user_id: str, email: str, db: AsyncSession
    ) -> str:
        """Solicita verificação de email (gera token)."""
        # Verifica se email já está em uso
        result = await db.execute(
            select(User).where(and_(User.email == email, User.id != user_id))
        )
        if result.scalar_one_or_none():
            raise ConflictError("Email já está em uso")

        # Gera token único
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Remove verificações anteriores pendentes
        await db.execute(
            select(EmailVerification).where(
                and_(
                    EmailVerification.user_id == user_id,
                    EmailVerification.email == email,
                )
            )
        )
        # Cria nova verificação
        verification = EmailVerification(
            user_id=user_id,
            email=email,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(verification)
        await db.commit()

        return token  # Retorna para enviar via email

    @staticmethod
    async def confirm_email_verification(
        user_id: str, email: str, token: str, db: AsyncSession
    ) -> None:
        """Confirma verificação de email."""
        token_hash = hash_token(token)

        result = await db.execute(
            select(EmailVerification).where(
                and_(
                    EmailVerification.user_id == user_id,
                    EmailVerification.email == email,
                    EmailVerification.token_hash == token_hash,
                    EmailVerification.expires_at > datetime.now(timezone.utc),
                )
            )
        )

        verification = result.scalar_one_or_none()

        if not verification:
            raise ValidationError("Token inválido ou expirado")

        # Atualiza verificação
        verification.status = "VERIFIED"
        verification.verified_at = datetime.now(timezone.utc)

        # Atualiza email do usuário
        user = await AuthService.get_user_by_id(user_id, db)
        user.email = email

        await db.commit()

    @staticmethod
    async def request_phone_verification(
        user_id: str, phone: str, db: AsyncSession
    ) -> str:
        """Solicita verificação de telefone (gera token)."""
        # Verifica se telefone já está em uso
        result = await db.execute(
            select(User).where(and_(User.celular == phone, User.id != user_id))
        )
        if result.scalar_one_or_none():
            raise ConflictError("Telefone já está em uso")

        # Gera token único
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Cria nova verificação
        verification = PhoneVerification(
            user_id=user_id,
            phone=phone,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(verification)
        await db.commit()

        return token  # Retorna para enviar via SMS/Telegram

    @staticmethod
    async def confirm_phone_verification(
        user_id: str, phone: str, token: str, db: AsyncSession
    ) -> None:
        """Confirma verificação de telefone."""
        token_hash = hash_token(token)

        result = await db.execute(
            select(PhoneVerification).where(
                and_(
                    PhoneVerification.user_id == user_id,
                    PhoneVerification.phone == phone,
                    PhoneVerification.token_hash == token_hash,
                    PhoneVerification.expires_at > datetime.now(timezone.utc),
                )
            )
        )

        verification = result.scalar_one_or_none()

        if not verification:
            raise ValidationError("Token inválido ou expirado")

        # Atualiza verificação
        verification.status = "VERIFIED"
        verification.verified_at = datetime.now(timezone.utc)

        # Atualiza telefone do usuário
        user = await AuthService.get_user_by_id(user_id, db)
        user.celular = phone

        await db.commit()

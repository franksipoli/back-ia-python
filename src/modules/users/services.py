"""Serviço de gerenciamento de usuários."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.models import User
from src.shared.exceptions import ConflictError, ForbiddenError, NotFoundError
from src.shared.security import hash_password


class UsersService:
    """Serviço de usuários."""

    @staticmethod
    async def create_user(
        name: str,
        email: str,
        cpf_cnpj: str,
        celular: str,
        role: str,
        password: str,
        db: AsyncSession,
    ) -> User:
        """Cria novo usuário (apenas ADMIN)."""
        # Verifica se email já existe
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ConflictError("Email já foi registrado")

        # Verifica se CPF/CNPJ já existe
        result = await db.execute(select(User).where(User.cpf_cnpj == cpf_cnpj))
        if result.scalar_one_or_none():
            raise ConflictError("CPF/CNPJ já foi registrado")

        # Verifica se celular já existe
        result = await db.execute(select(User).where(User.celular == celular))
        if result.scalar_one_or_none():
            raise ConflictError("Celular já foi registrado")

        # Cria usuário
        user = User(
            name=name,
            email=email,
            cpf_cnpj=cpf_cnpj,
            celular=celular,
            password_hash=hash_password(password),
            role=role,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
        """Busca usuário por ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("Usuário não encontrado")

        return user

    @staticmethod
    async def list_users(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[User], int]:
        """Lista usuarios com paginação (apenas ADMIN)."""
        # Total de usuários
        result = await db.execute(select(User))
        total = len(result.fetchall())

        # Usuários da página
        offset = (page - 1) * per_page

        result = await db.execute(
            select(User).offset(offset).limit(per_page).order_by(User.created_at.desc())
        )
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def update_user(
        user_id: str,
        is_active: bool | None = None,
        role: str | None = None,
        db: AsyncSession = None,
    ) -> User:
        """Atualiza usuário (apenas ADMIN pode atualizar outros usuários)."""
        user = await UsersService.get_user_by_id(user_id, db)

        if is_active is not None:
            user.is_active = is_active

        if role is not None:
            user.role = role

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete_user(user_id: str, db: AsyncSession, current_user_id: str) -> None:
        """Deleta usuário (apenas ADMIN, não pode deletar a si mesmo)."""
        if user_id == current_user_id:
            raise ForbiddenError("Você não pode deletar sua própria conta")

        user = await UsersService.get_user_by_id(user_id, db)

        await db.delete(user)
        await db.commit()

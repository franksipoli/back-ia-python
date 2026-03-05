"""Rotas de gerenciamento de usuários."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infra.database import get_db
from src.modules.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserDetailResponse,
    UserListResponse,
    UsersListPaginatedResponse,
)
from src.modules.users.services import UsersService
from src.shared.security import get_current_user, require_admin

router = APIRouter(prefix=f"/{settings.api_prefix}/users", tags=["Users"])


@router.get("", response_model=UsersListPaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os usuários (apenas ADMIN)."""
    users, total = await UsersService.list_users(db, page, per_page)

    pages = (total + per_page - 1) // per_page

    return UsersListPaginatedResponse(
        data=[
            UserListResponse(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém detalhes de um usuário."""
    # Usuário pode ver seu próprio perfil ou admin pode ver qualquer um
    if current_user["sub"] != user_id and current_user["role"] != "ADMIN":
        from src.shared.exceptions import ForbiddenError

        raise ForbiddenError("Você não tem permissão para acessar este usuário")

    user = await UsersService.get_user_by_id(user_id, db)

    return UserDetailResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        cpf_cnpj=user.cpf_cnpj,
        celular=user.celular,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Cria novo usuário (apenas ADMIN)."""
    user = await UsersService.create_user(
        name=request.name,
        email=request.email,
        cpf_cnpj=request.cpf_cnpj,
        celular=request.celular,
        role=request.role,
        password=request.password,
        db=db,
    )

    return UserDetailResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        cpf_cnpj=user.cpf_cnpj,
        celular=user.celular,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza usuário (apenas ADMIN)."""
    user = await UsersService.update_user(
        user_id=user_id,
        is_active=request.is_active,
        role=request.role,
        db=db,
    )

    return UserDetailResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        cpf_cnpj=user.cpf_cnpj,
        celular=user.celular,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Deleta usuário (apenas ADMIN)."""
    await UsersService.delete_user(user_id=user_id, db=db, current_user_id=current_user["sub"])

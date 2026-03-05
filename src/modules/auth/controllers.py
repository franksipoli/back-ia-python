"""Rotas de autenticação."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infra.database import get_db
from src.modules.auth.schemas import (
    AuthMeResponse,
    ChangePasswordRequest,
    EmailVerificationConfirmRequest,
    EmailVerificationRequest,
    LoginRequest,
    PhoneVerificationConfirmRequest,
    PhoneVerificationRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.modules.auth.services import AuthService
from src.shared.security import get_current_user

router = APIRouter(prefix=f"/{settings.api_prefix}/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Registra novo usuário."""
    user = await AuthService.register(
        name=request.name,
        email=request.email,
        cpf_cnpj=request.cpf_cnpj,
        celular=request.celular,
        password=request.password,
        db=db,
    )

    # Realiza login automático
    access_token, refresh_token = await AuthService.login(
        email=request.email,
        password=request.password,
        db=db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expires_in,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Realiza login do usuário."""
    access_token, refresh_token = await AuthService.login(
        email=request.email,
        password=request.password,
        db=db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Renova access token usando refresh token."""
    access_token = await AuthService.refresh_access_token(
        refresh_token=request.refresh_token,
        db=db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,
        expires_in=settings.jwt_expires_in,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Realiza logout revogando refresh token."""
    await AuthService.logout(
        refresh_token=request.refresh_token,
        db=db,
    )


@router.get("/me", response_model=AuthMeResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna dados do usuário autenticado."""
    user = await AuthService.get_user_by_id(current_user["sub"], db)

    return AuthMeResponse(
        user=UserResponse(
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
    )


@router.patch("/me/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Altera a senha do usuário autenticado."""
    await AuthService.change_password(
        user_id=current_user["sub"],
        current_password=request.current_password,
        new_password=request.new_password,
        db=db,
    )

    return {"message": "Senha alterada com sucesso"}


# ============================================================================
# Email Verification
# ============================================================================


@router.post("/verify/email/request")
async def request_email_verification(
    request: EmailVerificationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Solicita verificação de email (envia token)."""
    token = await AuthService.request_email_verification(
        user_id=current_user["sub"],
        email=request.email,
        db=db,
    )

    # TODO: Enviar token via email
    # await send_email(request.email, "Verificação de Email", token)

    return {
        "message": "Token de verificação enviado por email",
        "token": token,  # DEBUG: remover em produção
    }


@router.post("/verify/email/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_email_verification(
    request: EmailVerificationConfirmRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirma verificação de email."""
    await AuthService.confirm_email_verification(
        user_id=current_user["sub"],
        email=request.email,
        token=request.token,
        db=db,
    )


# ============================================================================
# Phone Verification
# ============================================================================


@router.post("/verify/phone/request")
async def request_phone_verification(
    request: PhoneVerificationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Solicita verificação de telefone (envia token via SMS/Telegram)."""
    token = await AuthService.request_phone_verification(
        user_id=current_user["sub"],
        phone=request.phone,
        db=db,
    )

    # TODO: Enviar token via SMS ou Telegram
    # await send_sms(request.phone, f"Seu código de verificação: {token}")

    return {
        "message": "Token de verificação enviado por SMS/Telegram",
        "token": token,  # DEBUG: remover em produção
    }


@router.post("/verify/phone/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_phone_verification(
    request: PhoneVerificationConfirmRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirma verificação de telefone."""
    await AuthService.confirm_phone_verification(
        user_id=current_user["sub"],
        phone=request.phone,
        token=request.token,
        db=db,
    )

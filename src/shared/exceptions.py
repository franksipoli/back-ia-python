"""Exceções customizadas da aplicação."""

from fastapi import HTTPException, status


class AppException(Exception):
    """Exceção base da aplicação."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Erro de validação."""

    def __init__(self, message: str | list[str]):
        if isinstance(message, list):
            message = "; ".join(message)
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(AppException):
    """Erro de autorização (sem credenciais válidas)."""

    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppException):
    """Erro de permissão (usuário autenticado mas sem permissão)."""

    def __init__(self, message: str = "Acesso proibido"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """Erro: recurso não encontrado."""

    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Erro: conflito (ex: email já existe)."""

    def __init__(self, message: str = "Conflito"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InternalServerError(AppException):
    """Erro interno do servidor."""

    def __init__(self, message: str = "Erro interno do servidor"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

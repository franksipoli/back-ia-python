"""Configuração da aplicação baseada em ambiente."""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # App
    python_env: Literal["development", "testing", "production"] = "development"
    port: int = 8000
    api_prefix: str = "v1"

    # JWT
    jwt_secret: str = "your-secret-key-change-me"
    jwt_expires_in: int = 3600  # 1 hora
    jwt_algorithm: str = "HS256"

    # Refresh Token
    refresh_token_expires_in: int = 604800  # 7 dias

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/back_ia_db"

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # Email/SMS (optional for future integration)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "your-email@example.com"
    smtp_password: str = "your-password"
    sms_provider: str = "twilio"
    sms_account_sid: str = "your-account-sid"
    sms_auth_token: str = "your-auth-token"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignora campos extras do .env


settings = Settings()

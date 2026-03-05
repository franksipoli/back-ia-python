"""Rotas de health check."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infra.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"/{settings.api_prefix}", tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Verifica saúde da aplicação."""
    # Testa conexão com banco
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "environment": settings.python_env,
        "version": "0.1.0",
        "database": db_status,
    }

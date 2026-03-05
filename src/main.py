"""Aplicação FastAPI principal."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.modules.auth.controllers import router as auth_router
from src.modules.health.controllers import router as health_router
from src.modules.users.controllers import router as users_router
from src.shared.exceptions import AppException
from src.shared.middleware import add_error_handler, add_logging_middleware

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    logger.info("Iniciando aplicação Back IA Python")
    yield
    logger.info("Finalizando aplicação Back IA Python")


app = FastAPI(
    title="Back IA Python API",
    description="Backend REST API com FastAPI, JWT, SQLAlchemy e PostgreSQL",
    version="0.1.0",
    docs_url=f"/{settings.api_prefix}/docs",
    openapi_url=f"/{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging e error handling
add_logging_middleware(app)
add_error_handler(app)


# Registra rotas dos módulos
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)


# Health check básico
@app.get(f"/{settings.api_prefix}/health", tags=["Health"])
async def health_check():
    """Verifica se a aplicação está saudável."""
    return {
        "status": "ok",
        "environment": settings.python_env,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Rota raiz."""
    return {
        "message": "Bem-vindo à Back IA Python API",
        "docs": f"http://localhost:{settings.port}/{settings.api_prefix}/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.python_env == "development",
    )

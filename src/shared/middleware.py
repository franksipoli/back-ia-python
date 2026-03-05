"""Middleware da aplicação."""

import json
import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.shared.exceptions import AppException

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware para logging estruturado."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Processa request com logging usando ASGI."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        start_time = time.time()
        method = scope.get("method")
        path = scope.get("path")
        query_string = scope.get("query_string", b"").decode()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                process_time = time.time() - start_time
                
                log_data = {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query_string": query_string,
                    "status_code": status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                }
                logger.info(json.dumps(log_data))
            
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                json.dumps({
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(exc),
                    "process_time_ms": round(process_time * 1000, 2),
                })
            )
            raise


def add_logging_middleware(app: FastAPI) -> None:
    """Adiciona middleware de logging à aplicação."""
    app.add_middleware(LoggingMiddleware)


def add_error_handler(app: FastAPI) -> None:
    """Adiciona handlers de erro à aplicação."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handler para exceções customizadas da aplicação."""
        request_id = getattr(request.state, "request_id", "unknown")

        error_response = {
            "statusCode": exc.status_code,
            "error": "Error",
            "message": exc.message,
            "path": str(request.url.path),
            "timestamp": json.dumps({}, default=str),
            "requestId": request_id,
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler para exceções genéricas."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        error_response = {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": "Ocorreu um erro interno no servidor",
            "path": str(request.url.path),
            "timestamp": json.dumps({}, default=str),
            "requestId": request_id,
        }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )

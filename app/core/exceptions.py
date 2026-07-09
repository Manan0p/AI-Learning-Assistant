from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from loguru import logger
from sqlalchemy.exc import NoResultFound


class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class LLMOutputError(AppError):
    def __init__(self, message: str = "The AI response could not be validated.") -> None:
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> ORJSONResponse:
        logger.warning("Application error: {}", exc.message)
        return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(NoResultFound)
    async def not_found_handler(_: Request, __: NoResultFound) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception) -> ORJSONResponse:
        logger.exception("Unhandled error: {}", exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

from __future__ import annotations

from src.application.errors import (
    ApplicationError,
    OperationAccessError,
    OperationNotFoundError,
    ProjectDisabledError,
    ProjectNotFoundError,
)


def map_exception_to_user_text(exc: Exception, fallback_text: str) -> str:
    if isinstance(exc, ProjectDisabledError):
        return "Проект отключен. Обратитесь к администратору."
    if isinstance(exc, (ProjectNotFoundError, OperationNotFoundError, OperationAccessError)):
        return "Операция больше недоступна."
    if isinstance(exc, ApplicationError):
        return "Не удалось выполнить операцию. Попробуйте позже."
    return fallback_text


def log_handler_exception(
    logger,
    action: str,
    exc: Exception,
    *,
    operation_id: int | None = None,
) -> None:
    logger.bind(operation_id=operation_id or "-").error(f"{action} failed: {exc}")

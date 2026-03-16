from __future__ import annotations

import sys
from typing import Any

from loguru import logger as _logger


def _patch_record(record: dict[str, Any]) -> None:
    extra = record["extra"]
    extra.setdefault("prefix", "app")
    extra.setdefault("prefix_color", "green")
    extra.setdefault("project_key", "-")
    extra.setdefault("operation_id", "-")
    extra.setdefault("sync_task_id", "-")


def _format_record(record: dict[str, Any]) -> str:
    color = record["extra"]["prefix_color"]
    return (
        f"<{color}>{{time:YYYY-MM-DD HH:mm:ss}}</{color}> | "
        "<level>{level:<8}</level> | "
        "<cyan>{extra[prefix]}</cyan> | "
        "<magenta>project={extra[project_key]}</magenta> | "
        "<yellow>operation={extra[operation_id]}</yellow> | "
        "<blue>sync={extra[sync_task_id]}</blue> | "
        "<level>{message}</level>\n{exception}"
    )


logger = _logger.patch(_patch_record)


def get_logger(
    prefix: str = "app",
    *,
    color: str = "green",
    project_key: str | None = None,
    operation_id: int | str | None = None,
    sync_task_id: int | str | None = None,
):
    if not logger._core.handlers:
        logger.add(
            lambda message: print(message, end="", file=sys.stdout),
            level="INFO",
            format=_format_record,
            colorize=True,
            backtrace=False,
            diagnose=False,
        )
    return logger.bind(
        prefix=prefix,
        prefix_color=color,
        project_key=project_key or "-",
        operation_id=operation_id or "-",
        sync_task_id=sync_task_id or "-",
    )

from __future__ import annotations

from dataclasses import dataclass

from src.domain.enums import SyncStatus


@dataclass(slots=True)
class SyncAttempt:
    sync_task_id: int
    status: SyncStatus
    id: int | None = None
    error_message: str | None = None

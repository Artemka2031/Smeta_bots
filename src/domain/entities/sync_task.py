from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import SyncStatus, SyncTaskType


@dataclass(slots=True)
class SyncTask:
    project_id: int
    operation_id: int
    task_type: SyncTaskType
    status: SyncStatus = SyncStatus.PENDING
    id: int | None = None
    payload: dict | None = None
    retry_count: int = 0
    max_retries: int = 10
    last_error: str | None = None
    next_retry_at: datetime | None = None
    locked_at: datetime | None = None
    finished_at: datetime | None = None

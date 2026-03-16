from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import OperationStatus, OperationType, SyncStatus, SyncTaskType


@dataclass(slots=True)
class DeleteOperationResult:
    operation_id: int
    project_id: int
    operation_type: OperationType
    status: OperationStatus
    deleted_at: datetime
    sync_task_id: int | None = None
    sync_status: SyncStatus | None = None
    sync_task_type: SyncTaskType | None = None

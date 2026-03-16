from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.domain.enums import OperationStatus, OperationType, SyncStatus, SyncTaskType


@dataclass(slots=True)
class CreateRepaymentCommand:
    project_key: str
    operation_date: date
    amount: Decimal
    creditor: str
    comment: str | None = None
    mark_synced: bool = False


@dataclass(slots=True)
class CreateRepaymentResult:
    operation_id: int
    sync_task_id: int
    project_id: int
    operation_type: OperationType
    operation_status: OperationStatus
    sync_status: SyncStatus
    sync_task_type: SyncTaskType

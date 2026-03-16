from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.domain.enums import OperationStatus, OperationType, SyncStatus, SyncTaskType


@dataclass(slots=True)
class CreateBorrowedExpenseCommand:
    project_key: str
    operation_date: date
    amount: Decimal
    chapter_code: str
    category_code: str
    creditor: str
    coefficient: Decimal
    comment: str | None = None
    subcategory_code: str | None = None
    mark_synced: bool = False


@dataclass(slots=True)
class CreateBorrowedExpenseResult:
    operation_id: int
    sync_task_id: int
    project_id: int
    operation_type: OperationType
    operation_status: OperationStatus
    sync_status: SyncStatus
    sync_task_type: SyncTaskType

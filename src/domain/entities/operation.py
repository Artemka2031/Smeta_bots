from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from src.domain.enums import OperationStatus, OperationType


@dataclass(slots=True)
class Operation:
    project_id: int
    operation_type: OperationType
    operation_date: date
    amount: Decimal
    status: OperationStatus = OperationStatus.PENDING_SYNC
    id: int | None = None
    comment: str | None = None
    chapter_code: str | None = None
    category_code: str | None = None
    subcategory_code: str | None = None
    coming_code: str | None = None
    creditor: str | None = None
    coefficient: Decimal | None = None
    deleted_at: datetime | None = None

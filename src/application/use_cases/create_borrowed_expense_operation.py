from __future__ import annotations

from datetime import datetime, timezone

from src.application.dto import CreateBorrowedExpenseCommand, CreateBorrowedExpenseResult
from src.application.errors import ProjectDisabledError, ProjectNotFoundError
from src.application.uow import UnitOfWork
from src.domain.entities import Operation, SyncTask
from src.domain.enums import OperationStatus, OperationType, SyncStatus, SyncTaskType


class CreateBorrowedExpenseOperation:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateBorrowedExpenseCommand) -> CreateBorrowedExpenseResult:
        async with self._uow as uow:
            project = await uow.projects.get_by_project_key(command.project_key)
            if project is None:
                raise ProjectNotFoundError(f"Project '{command.project_key}' not found")
            if not project.enabled:
                raise ProjectDisabledError(f"Project '{command.project_key}' is disabled")

            operation = await uow.operations.add(
                Operation(
                    project_id=project.id,
                    operation_type=OperationType.BORROWED_EXPENSE,
                    status=OperationStatus.SYNCED if command.mark_synced else OperationStatus.PENDING_SYNC,
                    operation_date=command.operation_date,
                    amount=command.amount,
                    chapter_code=command.chapter_code,
                    category_code=command.category_code,
                    subcategory_code=command.subcategory_code,
                    creditor=command.creditor,
                    coefficient=command.coefficient,
                    comment=command.comment,
                )
            )

            sync_task = await uow.sync_tasks.add(
                SyncTask(
                    project_id=project.id,
                    operation_id=operation.id,
                    task_type=SyncTaskType.APPLY_OPERATION,
                    status=SyncStatus.COMPLETED if command.mark_synced else SyncStatus.PENDING,
                    payload={
                        "operation_type": OperationType.BORROWED_EXPENSE.value,
                        "operation_id": operation.id,
                    },
                    finished_at=datetime.now(timezone.utc) if command.mark_synced else None,
                )
            )

            await uow.commit()

        return CreateBorrowedExpenseResult(
            operation_id=operation.id,
            sync_task_id=sync_task.id,
            project_id=project.id,
            operation_type=operation.operation_type,
            operation_status=operation.status,
            sync_status=sync_task.status,
            sync_task_type=sync_task.task_type,
        )

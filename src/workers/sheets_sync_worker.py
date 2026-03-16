from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from src.domain.entities import SyncAttempt
from src.domain.enums import OperationStatus, OperationType, SyncStatus, SyncTaskType
from src.domain.services import calculate_borrowing_breakdown
from src.interfaces.telegram.date_utils import format_sheet_date
from src.management.logging import get_logger


class SheetsSyncWorker:
    def __init__(
        self,
        project_key: str,
        sheets_gateway,
        uow_factory,
        poll_interval_seconds: float = 2.0,
        retry_base_seconds: int = 5,
    ) -> None:
        self._project_key = project_key
        self._sheets_gateway = sheets_gateway
        self._uow_factory = uow_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._retry_base_seconds = retry_base_seconds
        self._logger = get_logger("sync-worker", color="blue", project_key=project_key)

    async def run(self) -> None:
        while True:
            processed = await self.process_once()
            if not processed:
                await asyncio.sleep(self._poll_interval_seconds)

    async def process_once(self) -> bool:
        async with self._uow_factory() as uow:
            project = await uow.projects.get_by_project_key(self._project_key)
            if project is None or not project.enabled:
                return False

            sync_task = await uow.sync_tasks.claim_next(project.id)
            if sync_task is None:
                return False

            await uow.commit()

        try:
            await self._apply_task(sync_task)
        except Exception as exc:
            await self._mark_failed(sync_task, str(exc))
            self._logger.bind(
                sync_task_id=sync_task.id or "-",
                operation_id=sync_task.operation_id,
            ).error(f"Sync task failed: {exc}")
            return True

        await self._mark_completed(sync_task)
        return True

    async def _apply_task(self, sync_task) -> None:
        async with self._uow_factory() as uow:
            operation = await uow.operations.get_by_id(sync_task.operation_id)
            if operation is None:
                raise ValueError(f"Operation '{sync_task.operation_id}' not found")

        if sync_task.task_type == SyncTaskType.APPLY_OPERATION:
            await self._apply_operation(operation)
            return

        if sync_task.task_type == SyncTaskType.DELETE_OPERATION:
            await self._delete_operation(operation)
            return

        raise ValueError(f"Unsupported sync task type '{sync_task.task_type}'")

    async def _apply_operation(self, operation) -> None:
        if operation.status == OperationStatus.DELETED:
            return

        if operation.status == OperationStatus.SYNCED:
            return

        operation_date = format_sheet_date(operation.operation_date)

        if operation.operation_type == OperationType.EXPENSE:
            await self._sheets_gateway.update_expense_with_comment(
                operation.chapter_code,
                operation.subcategory_code or operation.category_code,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        if operation.operation_type == OperationType.COMING:
            await self._sheets_gateway.update_coming_with_comment(
                operation.chapter_code,
                operation.coming_code,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        if operation.operation_type == OperationType.BORROWED_EXPENSE:
            breakdown = calculate_borrowing_breakdown(
                operation.amount,
                operation.coefficient or operation.amount.__class__("1"),
            )

            await self._sheets_gateway.update_expense_with_comment(
                operation.chapter_code,
                operation.subcategory_code or operation.category_code,
                operation_date,
                breakdown.borrowing_amount,
                operation.comment,
            )
            await self._sheets_gateway.record_borrowing(
                operation.creditor,
                operation_date,
                operation.amount,
                operation.comment,
            )
            if breakdown.saving_amount > 0:
                await self._sheets_gateway.record_saving(
                    operation.creditor,
                    operation_date,
                    breakdown.saving_amount,
                    operation.comment,
                )
            return

        if operation.operation_type == OperationType.REPAYMENT:
            await self._sheets_gateway.record_repayment(
                operation.creditor,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        raise ValueError(f"Unsupported operation type '{operation.operation_type}'")

    async def _delete_operation(self, operation) -> None:
        if operation.status != OperationStatus.DELETED:
            return

        operation_date = format_sheet_date(operation.operation_date)

        if operation.operation_type == OperationType.EXPENSE:
            await self._sheets_gateway.remove_expense(
                operation.chapter_code,
                operation.subcategory_code or operation.category_code,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        if operation.operation_type == OperationType.COMING:
            await self._sheets_gateway.remove_coming(
                operation.chapter_code,
                operation.coming_code,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        if operation.operation_type == OperationType.BORROWED_EXPENSE:
            breakdown = calculate_borrowing_breakdown(
                operation.amount,
                operation.coefficient or operation.amount.__class__("1"),
            )

            await self._sheets_gateway.remove_expense(
                operation.chapter_code,
                operation.subcategory_code or operation.category_code,
                operation_date,
                breakdown.borrowing_amount,
                operation.comment,
            )
            await self._sheets_gateway.remove_borrowing(
                operation.creditor,
                operation_date,
                operation.amount,
                operation.comment,
            )
            if breakdown.saving_amount > 0:
                await self._sheets_gateway.remove_saving(
                    operation.creditor,
                    operation_date,
                    breakdown.saving_amount,
                    operation.comment,
                )
            return

        if operation.operation_type == OperationType.REPAYMENT:
            await self._sheets_gateway.remove_repayment(
                operation.creditor,
                operation_date,
                operation.amount,
                operation.comment,
            )
            return

        raise ValueError(f"Unsupported operation type '{operation.operation_type}'")

    async def _mark_completed(self, sync_task) -> None:
        finished_at = datetime.now(timezone.utc)

        async with self._uow_factory() as uow:
            operation = await uow.operations.get_by_id(sync_task.operation_id)
            if operation is None:
                raise ValueError(f"Operation '{sync_task.operation_id}' not found during completion")

            if sync_task.task_type == SyncTaskType.APPLY_OPERATION and operation.status != OperationStatus.DELETED:
                operation.status = OperationStatus.SYNCED
            await uow.operations.update(operation)

            sync_task.status = SyncStatus.COMPLETED
            sync_task.finished_at = finished_at
            sync_task.locked_at = None
            sync_task.next_retry_at = None
            sync_task.last_error = None
            await uow.sync_tasks.update(sync_task)

            await uow.sync_attempts.add(
                SyncAttempt(
                    sync_task_id=sync_task.id,
                    status=SyncStatus.COMPLETED,
                )
            )
            await uow.commit()
        self._logger.bind(
            sync_task_id=sync_task.id or "-",
            operation_id=sync_task.operation_id,
        ).info("Sync task completed")

    async def _mark_failed(self, sync_task, error_message: str) -> None:
        retry_count = sync_task.retry_count + 1
        next_retry_at = None
        if retry_count < sync_task.max_retries:
            delay_seconds = self._retry_base_seconds * (2 ** (retry_count - 1))
            next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

        async with self._uow_factory() as uow:
            operation = await uow.operations.get_by_id(sync_task.operation_id)
            if operation is not None and sync_task.task_type == SyncTaskType.APPLY_OPERATION:
                operation.status = OperationStatus.SYNC_FAILED
                await uow.operations.update(operation)

            sync_task.status = SyncStatus.FAILED
            sync_task.retry_count = retry_count
            sync_task.last_error = error_message
            sync_task.next_retry_at = next_retry_at
            sync_task.locked_at = None
            await uow.sync_tasks.update(sync_task)

            await uow.sync_attempts.add(
                SyncAttempt(
                    sync_task_id=sync_task.id,
                    status=SyncStatus.FAILED,
                    error_message=error_message,
                )
            )
            await uow.commit()
        self._logger.bind(
            sync_task_id=sync_task.id or "-",
            operation_id=sync_task.operation_id,
        ).warning(f"Sync task marked as failed: {error_message}")

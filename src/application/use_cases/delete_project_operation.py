from __future__ import annotations

from datetime import datetime, timezone

from src.application.dto import DeleteOperationResult
from src.application.errors import OperationAccessError, OperationNotFoundError, ProjectNotFoundError
from src.application.uow import UnitOfWork
from src.domain.entities import SyncTask
from src.domain.enums import OperationStatus, SyncStatus, SyncTaskType


class DeleteProjectOperation:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, project_key: str, operation_id: int) -> DeleteOperationResult:
        async with self._uow as uow:
            project = await uow.projects.get_by_project_key(project_key)
            if project is None:
                raise ProjectNotFoundError(f"Project '{project_key}' not found")

            operation = await uow.operations.get_by_id(operation_id)
            if operation is None:
                raise OperationNotFoundError(f"Operation '{operation_id}' not found")
            if operation.project_id != project.id:
                raise OperationAccessError(
                    f"Operation '{operation_id}' does not belong to project '{project_key}'"
                )

            previous_status = operation.status
            deleted_at = datetime.now(timezone.utc)
            operation.status = OperationStatus.DELETED
            operation.deleted_at = deleted_at

            updated_operation = await uow.operations.update(operation)
            sync_task = None
            if previous_status == OperationStatus.SYNCED:
                sync_task = await uow.sync_tasks.add(
                    SyncTask(
                        project_id=project.id,
                        operation_id=updated_operation.id,
                        task_type=SyncTaskType.DELETE_OPERATION,
                        status=SyncStatus.PENDING,
                        payload={
                            "operation_type": updated_operation.operation_type.value,
                            "operation_id": updated_operation.id,
                        },
                    )
                )
            await uow.commit()

        return DeleteOperationResult(
            operation_id=updated_operation.id,
            project_id=updated_operation.project_id,
            operation_type=updated_operation.operation_type,
            status=updated_operation.status,
            deleted_at=deleted_at,
            sync_task_id=sync_task.id if sync_task is not None else None,
            sync_status=sync_task.status if sync_task is not None else None,
            sync_task_type=sync_task.task_type if sync_task is not None else None,
        )

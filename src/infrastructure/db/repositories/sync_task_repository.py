from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import SyncTask
from src.domain.enums import SyncStatus
from src.infrastructure.db.models import SyncTaskModel


def _to_entity(model: SyncTaskModel) -> SyncTask:
    return SyncTask(
        id=model.id,
        project_id=model.project_id,
        operation_id=model.operation_id,
        task_type=model.task_type,
        status=model.status,
        payload=model.payload,
        retry_count=model.retry_count,
        max_retries=model.max_retries,
        last_error=model.last_error,
        next_retry_at=model.next_retry_at,
        locked_at=model.locked_at,
        finished_at=model.finished_at,
    )


class SqlAlchemySyncTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._lock_timeout = timedelta(minutes=10)

    async def add(self, sync_task: SyncTask) -> SyncTask:
        model = SyncTaskModel(
            project_id=sync_task.project_id,
            operation_id=sync_task.operation_id,
            task_type=sync_task.task_type,
            status=sync_task.status,
            payload=sync_task.payload,
            retry_count=sync_task.retry_count,
            max_retries=sync_task.max_retries,
            last_error=sync_task.last_error,
            next_retry_at=sync_task.next_retry_at,
            locked_at=sync_task.locked_at,
            finished_at=sync_task.finished_at,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def claim_next(self, project_id: int) -> SyncTask | None:
        now = datetime.now(timezone.utc)
        stale_lock_threshold = now - self._lock_timeout
        result = await self._session.execute(
            select(SyncTaskModel)
            .where(
                SyncTaskModel.project_id == project_id,
                or_(
                    SyncTaskModel.status.in_([SyncStatus.PENDING, SyncStatus.FAILED]),
                    (
                        (SyncTaskModel.status == SyncStatus.IN_PROGRESS)
                        & SyncTaskModel.locked_at.is_not(None)
                        & (SyncTaskModel.locked_at <= stale_lock_threshold)
                    ),
                ),
                or_(
                    SyncTaskModel.status == SyncStatus.IN_PROGRESS,
                    SyncTaskModel.next_retry_at.is_(None),
                    SyncTaskModel.next_retry_at <= now,
                ),
            )
            .order_by(SyncTaskModel.id.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.status = SyncStatus.IN_PROGRESS
        model.locked_at = now
        model.last_error = None
        await self._session.flush()
        return _to_entity(model)

    async def update(self, sync_task: SyncTask) -> SyncTask:
        if sync_task.id is None:
            raise ValueError("SyncTask id is required for update")

        model = await self._session.get(SyncTaskModel, sync_task.id)
        if model is None:
            raise ValueError(f"SyncTask '{sync_task.id}' not found")

        model.status = sync_task.status
        model.payload = sync_task.payload
        model.retry_count = sync_task.retry_count
        model.max_retries = sync_task.max_retries
        model.last_error = sync_task.last_error
        model.next_retry_at = sync_task.next_retry_at
        model.locked_at = sync_task.locked_at
        model.finished_at = sync_task.finished_at
        await self._session.flush()
        return _to_entity(model)

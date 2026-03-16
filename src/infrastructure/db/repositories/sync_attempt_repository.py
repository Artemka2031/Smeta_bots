from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import SyncAttempt
from src.infrastructure.db.models import SyncAttemptModel


def _to_entity(model: SyncAttemptModel) -> SyncAttempt:
    return SyncAttempt(
        id=model.id,
        sync_task_id=model.sync_task_id,
        status=model.status,
        error_message=model.error_message,
    )


class SqlAlchemySyncAttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, attempt: SyncAttempt) -> SyncAttempt:
        model = SyncAttemptModel(
            sync_task_id=attempt.sync_task_id,
            status=attempt.status,
            error_message=attempt.error_message,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

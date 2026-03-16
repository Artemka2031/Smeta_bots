from __future__ import annotations

from typing import Protocol

from src.domain.entities import SyncTask


class SyncTaskRepository(Protocol):
    async def add(self, sync_task: SyncTask) -> SyncTask: ...

    async def claim_next(self, project_id: int) -> SyncTask | None: ...

    async def update(self, sync_task: SyncTask) -> SyncTask: ...

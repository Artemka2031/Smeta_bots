from __future__ import annotations

from typing import Protocol

from src.domain.repositories import OperationRepository, ProjectRepository, SyncAttemptRepository, SyncTaskRepository


class UnitOfWork(Protocol):
    projects: ProjectRepository
    operations: OperationRepository
    sync_attempts: SyncAttemptRepository
    sync_tasks: SyncTaskRepository

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def flush(self) -> None: ...

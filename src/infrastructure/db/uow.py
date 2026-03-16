from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.db.repositories import (
    SqlAlchemyOperationRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemySyncAttemptRepository,
    SqlAlchemySyncTaskRepository,
)
from src.management.settings import Settings, get_settings
from .session import get_session_factory


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        settings: Settings | None = None,
    ) -> None:
        active_settings = settings or get_settings()
        self._session_factory = session_factory or get_session_factory(active_settings)
        self.session: AsyncSession | None = None
        self.projects = None
        self.operations = None
        self.sync_attempts = None
        self.sync_tasks = None

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.operations = SqlAlchemyOperationRepository(self.session)
        self.sync_attempts = SqlAlchemySyncAttemptRepository(self.session)
        self.sync_tasks = SqlAlchemySyncTaskRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return

        if exc:
            await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.rollback()

    async def flush(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.flush()

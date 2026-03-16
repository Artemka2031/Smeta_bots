from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.base import Base
from src.infrastructure.db.models import OperationModel, ProjectModel, SyncAttemptModel, SyncTaskModel
from src.management.settings import Settings, get_settings


@lru_cache(maxsize=1)
def get_engine(database_url: str, echo: bool) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
    )


def get_session_factory(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    active_settings = settings or get_settings()
    engine = get_engine(active_settings.database_url, active_settings.sqlalchemy_echo)
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_models(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    engine = get_engine(active_settings.database_url, active_settings.sqlalchemy_echo)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_engine(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    engine = get_engine(active_settings.database_url, active_settings.sqlalchemy_echo)
    await engine.dispose()

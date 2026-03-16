from __future__ import annotations

from src.management.settings import Settings, get_settings

from .session import init_models


async def bootstrap_database(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    await init_models(active_settings)

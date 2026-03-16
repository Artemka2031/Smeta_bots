from __future__ import annotations

from typing import Protocol

from src.domain.entities import SyncAttempt


class SyncAttemptRepository(Protocol):
    async def add(self, attempt: SyncAttempt) -> SyncAttempt: ...

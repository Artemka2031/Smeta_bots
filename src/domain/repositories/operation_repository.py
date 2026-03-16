from __future__ import annotations

from typing import Protocol

from src.domain.entities import Operation


class OperationRepository(Protocol):
    async def add(self, operation: Operation) -> Operation: ...

    async def get_by_id(self, operation_id: int) -> Operation | None: ...

    async def update(self, operation: Operation) -> Operation: ...

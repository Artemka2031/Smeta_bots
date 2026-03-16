from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Operation
from src.infrastructure.db.models import OperationModel


def _to_entity(model: OperationModel) -> Operation:
    return Operation(
        id=model.id,
        project_id=model.project_id,
        operation_type=model.operation_type,
        status=model.status,
        operation_date=model.operation_date,
        amount=model.amount,
        comment=model.comment,
        chapter_code=model.chapter_code,
        category_code=model.category_code,
        subcategory_code=model.subcategory_code,
        coming_code=model.coming_code,
        creditor=model.creditor,
        coefficient=model.coefficient,
        deleted_at=model.deleted_at,
    )


class SqlAlchemyOperationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, operation: Operation) -> Operation:
        model = OperationModel(
            project_id=operation.project_id,
            operation_type=operation.operation_type,
            status=operation.status,
            operation_date=operation.operation_date,
            amount=operation.amount,
            comment=operation.comment,
            chapter_code=operation.chapter_code,
            category_code=operation.category_code,
            subcategory_code=operation.subcategory_code,
            coming_code=operation.coming_code,
            creditor=operation.creditor,
            coefficient=operation.coefficient,
            deleted_at=operation.deleted_at,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def get_by_id(self, operation_id: int) -> Operation | None:
        result = await self._session.execute(
            select(OperationModel).where(OperationModel.id == operation_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _to_entity(model)

    async def update(self, operation: Operation) -> Operation:
        if operation.id is None:
            raise ValueError("Operation id is required for update")

        model = await self._session.get(OperationModel, operation.id)
        if model is None:
            raise ValueError(f"Operation '{operation.id}' not found")

        model.status = operation.status
        model.operation_date = operation.operation_date
        model.amount = operation.amount
        model.comment = operation.comment
        model.chapter_code = operation.chapter_code
        model.category_code = operation.category_code
        model.subcategory_code = operation.subcategory_code
        model.coming_code = operation.coming_code
        model.creditor = operation.creditor
        model.coefficient = operation.coefficient
        model.deleted_at = operation.deleted_at

        await self._session.flush()
        return _to_entity(model)

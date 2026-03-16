from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Project
from src.infrastructure.db.models import ProjectModel


def _to_entity(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        project_key=model.project_key,
        name=model.name,
        bot_token=model.bot_token,
        spreadsheet_url=model.spreadsheet_url,
        enabled=model.enabled,
    )


class SqlAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, project_id: int) -> Project | None:
        model = await self._session.get(ProjectModel, project_id)
        if model is None:
            return None
        return _to_entity(model)

    async def get_by_project_key(self, project_key: str) -> Project | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.project_key == project_key)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _to_entity(model)

    async def add(self, project: Project) -> Project:
        model = ProjectModel(
            project_key=project.project_key,
            name=project.name,
            bot_token=project.bot_token,
            spreadsheet_url=project.spreadsheet_url,
            enabled=project.enabled,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def list_active(self) -> list[Project]:
        result = await self._session.execute(
            select(ProjectModel)
            .where(ProjectModel.enabled.is_(True))
            .order_by(ProjectModel.id.asc())
        )
        return [_to_entity(model) for model in result.scalars().all()]

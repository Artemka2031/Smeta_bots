from __future__ import annotations

from src.infrastructure.db.session import init_models
from src.infrastructure.db.repositories import SqlAlchemyProjectRepository
from src.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.domain.entities import Project

from .settings import ProjectDefinition, RuntimeProject, Settings, get_settings


def load_project_catalog(settings: Settings | None = None) -> list[ProjectDefinition]:
    active_settings = settings or get_settings()
    return active_settings.load_project_catalog()


async def seed_projects(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    await init_models(active_settings)

    async with SqlAlchemyUnitOfWork(settings=active_settings) as uow:
        repository = SqlAlchemyProjectRepository(uow.session)

        for project in active_settings.load_runtime_projects():
            existing_project = await repository.get_by_project_key(project.project_key)
            if existing_project is not None:
                continue

            await repository.add(
                Project(
                    project_key=project.project_key,
                    name=project.name,
                    bot_token=project.token,
                    spreadsheet_url=project.url,
                    enabled=project.enabled,
                )
            )

        await uow.commit()


async def load_runtime_projects(settings: Settings | None = None) -> list[dict[str, object]]:
    active_settings = settings or get_settings()
    await seed_projects(active_settings)

    async with SqlAlchemyUnitOfWork(settings=active_settings) as uow:
        repository = SqlAlchemyProjectRepository(uow.session)
        projects = await repository.list_active()

    runtime_catalog = {
        project.project_key: project
        for project in active_settings.load_runtime_projects()
    }

    runtime_projects: list[dict[str, object]] = []
    for project in projects:
        metadata = runtime_catalog.get(project.project_key)
        runtime_projects.append(
            RuntimeProject(
                project_key=project.project_key,
                name=project.name,
                token=project.bot_token,
                url=project.spreadsheet_url,
                enabled=project.enabled,
                work_chat=metadata.work_chat if metadata is not None else None,
                bot_link=metadata.bot_link if metadata is not None else None,
            ).to_runtime_dict()
        )

    return runtime_projects

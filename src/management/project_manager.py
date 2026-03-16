from __future__ import annotations

import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.interfaces.telegram.project_bot import ProjectBot
from src.interfaces.telegram.setup import setup_routers
from src.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.workers import SheetsSyncWorker

from .bootstrap import load_runtime_projects
from .logging import get_logger
from .settings import get_settings


class ProjectManager:
    def __init__(self) -> None:
        self.startup_delay_seconds = 3
        self.settings = get_settings()
        self.logger = get_logger("manager", color="green")

    async def initialize_projects(self) -> list[dict[str, object]]:
        projects = await load_runtime_projects(self.settings)
        initialized_projects: list[dict[str, object]] = []
        service_account_json = self.settings.google_credentials_payload

        for project in projects:
            try:
                initialized_projects.append(
                    {
                        "project_key": project["project_key"],
                        "name": project["name"],
                        "token": project["token"],
                        "google_sheet": project["url"],
                        "service_account_json": service_account_json,
                    }
                )
                self.logger.info(
                    f"Проект {project['name']} успешно инициализирован с Google Sheet {project['url']}"
                )
            except Exception as exc:
                self.logger.error(f"Ошибка при инициализации проекта {project['name']}: {exc}")

        return initialized_projects

    async def create_bot_instance(self, project: dict[str, object]) -> tuple[Dispatcher, ProjectBot]:
        bot = ProjectBot(
            token=project["token"],
            project_key=project["project_key"],
            project_name=project["name"],
            google_sheet_path=project["google_sheet"],
            service_account_json=project["service_account_json"],
        )
        logger = bot.logger
        logger.info(f"Инициализация бота с Google Sheet {project['google_sheet']}")

        dispatcher = Dispatcher(bot=bot, storage=MemoryStorage())
        await setup_routers(dispatcher, bot)

        logger.info("Бот инициализирован и настроен")
        return dispatcher, bot

    async def run_bot(self, project: dict[str, object]) -> None:
        dispatcher, bot = await self.create_bot_instance(project)
        logger = bot.logger
        logger.info(f"Запуск бота '{project['name']}'")
        sync_worker_task = None

        if bot.project_key and bot.sheets_gateway:
            sync_worker = SheetsSyncWorker(
                project_key=bot.project_key,
                sheets_gateway=bot.sheets_gateway,
                uow_factory=SqlAlchemyUnitOfWork,
            )
            sync_worker_task = asyncio.create_task(sync_worker.run(), name=f"sync-worker:{bot.project_key}")

        try:
            await dispatcher.start_polling(bot)
        finally:
            if sync_worker_task is not None:
                sync_worker_task.cancel()
                await asyncio.gather(sync_worker_task, return_exceptions=True)

    async def run_all_bots(self) -> None:
        all_projects = await self.initialize_projects()
        tasks = []

        for index, project in enumerate(all_projects, start=1):
            self.logger.info(f"Запуск проекта {index}/{len(all_projects)}: {project['name']}")
            tasks.append(asyncio.create_task(self.run_bot(project), name=project["name"]))

            if index < len(all_projects):
                self.logger.info(f"Ожидание {self.startup_delay_seconds} сек. перед запуском следующего проекта")
                await asyncio.sleep(self.startup_delay_seconds)

        await asyncio.gather(*tasks)

    def run(self) -> None:
        try:
            asyncio.run(self.run_all_bots())
        except Exception as exc:
            self.logger.error(f"Ошибка при запуске ботов: {exc}")

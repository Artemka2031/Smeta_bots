import asyncio
import logging
import os
from pathlib import Path

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.create_bot import ProjectBot
from Bot.run_bot import setup_routers
from config import projects


class ProjectManager:
    def __init__(self):
        self.startup_delay_seconds = 3
        self.logger = self.setup_logging()

    def setup_logging(self):
        """
        Настройка логгера.
        """
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logger

    def resolve_paths(self, project):
        """
        Метод для генерации пути к файлам базы данных и Google Sheets на основе названия базы данных.
        """
        db_name = project['db']  # Название базы данных из конфигурации
        google_sheet_url = project['url']  # URL для Google Sheets

        base_dir = Path(__file__).resolve().parent / "Data"
        base_dir.mkdir(parents=True, exist_ok=True)

        # Генерация полного пути к базе данных на основе названия базы данных
        db_full_path = base_dir / f"{db_name}.db"

        # Путь к файлу с учетными данными Google Sheets
        credentials_file = project.get('credentials_file', base_dir.parent / "GoogleSheets" / "creds.json")

        # Логируем информацию о пути
        self.logger.info(
            f"Настроены пути для проекта {project['name']}: БД {db_full_path}, Google Sheet {google_sheet_url}, credentials {credentials_file}")

        return db_full_path, google_sheet_url, credentials_file

    def initialize_projects(self):
        """
        Инициализация всех проектов и подготовка их конфигураций.
        """
        initialized_projects = []
        for project in projects:
            try:
                db_full_path, google_sheet_path, credentials_file = self.resolve_paths(project)
                initialized_project = {
                    "name": project['name'],
                    "token": project['token'],
                    "db": db_full_path,
                    "google_sheet": google_sheet_path,
                    "credentials_file": credentials_file
                }
                initialized_projects.append(initialized_project)
                self.logger.info(f"Проект {project['name']} успешно инициализирован")
            except Exception as e:
                self.logger.error(f"Ошибка при инициализации проекта {project['name']}: {e}")
        return initialized_projects

    async def create_bot_instance(self, project):
        """
        Создание экземпляра бота и его настройка.
        """
        bot = ProjectBot(
            token=project['token'],
            project_name=project['name'],
            google_sheet_path=project['google_sheet'],
            database_path=project['db'],
            credentials_file=project['credentials_file']
        )
        logger = bot.logger

        logger.info(
            f"Инициализация бота с токеном {project['token']}, Google Sheet {project['google_sheet']} и базой данных {project['db']}")

        storage = MemoryStorage()
        dp = Dispatcher(bot=bot, storage=storage)

        await setup_routers(dp, bot)

        logger.info("Бот инициализирован и настроен")
        return dp, bot

    async def run_bot(self, project):
        """
        Запуск бота для конкретного проекта.
        """
        dp, bot = await self.create_bot_instance(project)
        logger = bot.logger
        logger.info(f"Запуск бота '{project['name']}'")

        await dp.start_polling(bot)

    async def run_all_bots(self):
        """
        Запуск всех ботов из списка проектов.
        """
        all_projects = self.initialize_projects()
        tasks = []

        for index, project in enumerate(all_projects, start=1):
            self.logger.info(f"Запуск проекта {index}/{len(all_projects)}: {project['name']}")
            tasks.append(asyncio.create_task(self.run_bot(project), name=project["name"]))

            if index < len(all_projects):
                self.logger.info(
                    f"Ожидание {self.startup_delay_seconds} сек. перед запуском следующего проекта"
                )
                await asyncio.sleep(self.startup_delay_seconds)

        await asyncio.gather(*tasks)

    def run(self):
        """
        Основной метод для запуска всех проектов.
        """
        try:
            asyncio.run(self.run_all_bots())
        except Exception as e:
            self.logger.error(f"Ошибка при запуске ботов: {e}")

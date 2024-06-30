import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.create_bot import ProjectBot
from Bot.run_bot import setup_routers
from config import projects


# Создание и настройка экземпляра бота
async def create_bot_instance(project):
    logger = logging.getLogger(project['name'])
    logger.info(f"Инициализация бота с токеном {project['token']}, Google Sheet {project['url']} и базой данных {project['db']}")

    bot = ProjectBot(token=project['token'], project_name=project['name'], google_sheet_path=project['url'], database_path=project['db'])
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    await setup_routers(dp, bot)

    logger.info("Бот инициализирован и настроен")
    return dp, bot


# Запуск бота
async def run_bot(project):
    logger = logging.getLogger(project['name'])
    logger.info(f"Запуск бота '{project['name']}'")

    dp, bot = await create_bot_instance(project)
    await dp.start_polling(bot)


# Основная функция для запуска всех ботов
async def main():
    logger = logging.getLogger(__name__)
    logger.info("Запуск основной функции")

    logger.info(f"Запуск ботов")

    tasks = [run_bot(project) for project in projects]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

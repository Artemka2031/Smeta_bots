import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.create_bot import ProjectBot
from Bot.run_bot import setup_routers
from config import projects
from logger import setup_logging


# Создание и настройка экземпляра бота
async def create_bot_instance(token, google_sheet_url, database_path):
    logger = logging.getLogger(__name__)
    logger.info(f"Инициализация бота с токеном {token}, Google Sheet {google_sheet_url} и базой данных {database_path}")

    bot = ProjectBot(token=token, google_sheet_path=google_sheet_url, database_path=database_path)
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    await setup_routers(dp, bot)

    logger.info("Бот инициализирован и настроен")
    return dp, bot


# Запуск бота
async def run_bot(token, google_sheet_url, database_path):
    logger = logging.getLogger(__name__)
    logger.info(f"Запуск бота с Google Sheet {google_sheet_url} и базой данных {database_path}")

    dp, bot = await create_bot_instance(token, google_sheet_url, database_path)
    await dp.start_polling(bot)


# Основная функция для запуска всех ботов
async def main():
    logger = setup_logging()
    logger.info("Запуск основной функции")

    logger.info(f"Запуск ботов с конфигурациями: {projects}")

    tasks = [run_bot(project['token'], project['url'], project['db']) for project in projects]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

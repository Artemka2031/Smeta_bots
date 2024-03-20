import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.create_bot import ProjectBot  # Предполагается, что ProjectBot уже настроен для работы с Google Sheets
from Bot.run_bot import setup_routers


# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Логирование настроено")
    return logger


# Создание и настройка экземпляра бота
async def create_bot_instance(token, google_sheet_url):
    logger = logging.getLogger(__name__)
    logger.info(f"Инициализация бота с токеном {token} и Google Sheet {google_sheet_url}")

    bot = ProjectBot(token=token, google_sheet_path=google_sheet_url)
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    await setup_routers(dp, bot)

    logger.info("Бот инициализирован и настроен")
    return dp, bot


# Запуск бота
async def run_bot(token, google_sheet_url):
    logger = logging.getLogger(__name__)
    logger.info(f"Запуск бота с Google Sheet {google_sheet_url}")

    dp, bot = await create_bot_instance(token, google_sheet_url)
    await dp.start_polling(bot)


# Основная функция для запуска всех ботов
async def main():
    logger = setup_logging()
    logger.info("Запуск основной функции")

    projects = [
        {"token": "6999923210:AAHB6YtJLw7J8CWH3HKPD3sf6MiF-NkZpzU",
         "url": "https://docs.google.com/spreadsheets/d/1ksrGs8NqLaqH7WXKu2Dv1n294Oj32bB_6oYVQ0GKh54"}
    ]

    logger.info(f"Запуск ботов с конфигурациями: {projects}")

    tasks = [run_bot(project['token'], project['url']) for project in projects]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

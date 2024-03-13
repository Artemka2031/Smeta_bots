import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.run_bot import setup_routers
from Database.create_db import create_tables_with_drop
from Database.db_base import DatabaseManager


# Настройка логирования
def setup_logging():
    # Настройка базовой конфигурации логгера
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Добавление StreamHandler для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info("Логирование настроено")
    return logger


# Создание и настройка экземпляра бота
async def create_bot_instance(token, database_path):
    logger = logging.getLogger(__name__)
    logger.info(f"Инициализация бота с токеном {token} и базой данных {database_path}")

    # Установка базы данных для этого экземпляра
    DatabaseManager.set_database(database_path)

    # Проверка и создание таблиц, если они еще не созданы
    create_tables_with_drop()

    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    await setup_routers(dp, bot)

    logger.info("Бот инициализирован и настроен")
    return dp, bot


# Запуск бота
async def run_bot(token, db_name):
    logger = logging.getLogger(__name__)
    database_path = f'Data/{db_name}'
    logger.info(f"Запуск бота с базой данных {database_path}")

    dp, bot = await create_bot_instance(token, database_path)
    await dp.start_polling(bot)


# Основная функция для запуска всех ботов
async def main():
    logger = setup_logging()
    logger.info("Запуск основной функции")

    projects = [
        {"token": "6397282799:AAG-kCn6jHua9W9y48L20K_IDM-5kPEY3P0", "database_name": "project_1.db"},
        {"token": "6780094138:AAGqgwm5-RNuXOWGfvtGGDCXWaYsQbJWLns", "database_name": "project_2.db"}
    ]

    logger.info(f"Запуск ботов с конфигурациями: {projects}")

    tasks = [run_bot(project['token'], project['database_name']) for project in projects]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())

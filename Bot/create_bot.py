import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from peewee import SqliteDatabase

from Database.db_base import Expense
from GoogleSheets import GoogleSheets
from .commands import BotCommands


class ProjectBot(Bot):
    def __init__(self, token, google_sheet_path=None, database_path=None):
        super().__init__(token, parse_mode=ParseMode.HTML)
        if google_sheet_path:
            self.google_sheets = GoogleSheets(google_sheet_path)

        self.database = SqliteDatabase(database_path) if database_path else None

        # Привязка модели Expense к базе данных
        Expense._meta.database = self.database

        if google_sheet_path:
            # Здесь должна быть логика инициализации Google Sheets, если это необходимо
            pass

        # Создание таблиц в базе данных, если они ещё не созданы
        if self.database:
            self.database.connect()
            self.database.create_tables([Expense], safe=True)

    @staticmethod
    async def record_expense_operation(chapter_code, category_code_to_use, date, amount, comment):
        """
        Сохранение информации о расходной операции в базу данных.
        """
        try:
            expense_entry = Expense.create(
                date=date,
                chapter_code=chapter_code,
                category_code_to_use=category_code_to_use,
                amount=amount,
                comment=comment
            )
            expense_entry.save()
            logging.info(f"Расход успешно добавлен в базу данных c ID {expense_entry.id}")
            return expense_entry.id
        except Exception as e:
            logging.error(f"Ошибка при добавлении расхода в базу данных: {e}")

    @staticmethod
    async def record_debt_repayment(creditor, date, amount, comment):
        """
        Сохранение информации о возврате долга в базу данных.
        """
        try:
            debt_repayment_entry = Expense.create(
                date=date,
                creditor=creditor,
                amount=amount,
                comment=comment
            )
            debt_repayment_entry.save()
            logging.info(f"Возврат долга успешно добавлен в базу данных c ID {debt_repayment_entry.id}")
            return debt_repayment_entry.id
        except Exception as e:
            logging.error(f"Ошибка при добавлении возврата долга в базу данных: {e}")

    @staticmethod
    async def record_operation(date, creditor, chapter_code, category_code_to_use, amount, coefficient, comment):
        try:
            # Создание записи в базе данных
            expense_entry = Expense.create(
                date=date,
                creditor=creditor,
                chapter_code=chapter_code,
                category_code_to_use=category_code_to_use,
                amount=amount,
                coefficient=coefficient,
                comment=comment
            )

            logging.info(f"Операция успешно добавлена в базу данных c ID {expense_entry.id}")

            # Возвращаем созданную запись и экономию, если она есть
            return expense_entry.id

        except Exception as e:
            logging.error(f"Ошибка при добавлении операции в базу данных: {e}")
            return None

    async def get_expense_by_id(self, operation_id):
        """
        Получение данных о расходе по id операции.
        """
        expense = Expense.get_or_none(Expense.id == operation_id)
        if not expense:
            logging.error(f"Запись с ID {operation_id} не найдена.")
            return None
        return expense


def set_commands(commands: BotCommands):
    for params in commands:
        print(params)

import time
from datetime import datetime

from aiogram.filters import Filter
from aiogram.types import Message


class CheckDate(Filter):
    def __init__(self, date: str) -> None:
        self.date = date

    async def __call__(self, message: Message) -> bool:
        self.date = message.text

        try:
            valid_date = time.strptime(self.date, '%d.%m.%y')

            # Проверка года
            if not (2022 <= valid_date.tm_year <= 2030):
                return True  # Год не входит в диапазон от 2022 до 2030

            # Преобразование введенной даты в объект datetime
            input_datetime = datetime(valid_date.tm_year, valid_date.tm_mon, valid_date.tm_mday)

            # Получение текущей даты
            current_datetime = datetime.now()

            # Проверка, что введенная дата не больше текущей
            if input_datetime > current_datetime:
                return True  # Введенная дата больше текущей даты

        except ValueError:
            return True  # Некорректный формат даты

        return False  # Дата прошла все проверки

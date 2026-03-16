from datetime import datetime

from aiogram.filters import Filter
from aiogram.types import Message

from src.interfaces.telegram.date_utils import INPUT_DATE_FORMAT


class CheckDate(Filter):
    def __init__(self, _: str) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        try:
            input_datetime = datetime.strptime(message.text, INPUT_DATE_FORMAT)
            if not (2022 <= input_datetime.year <= 2100):
                return True
            if input_datetime.date() > datetime.now().date():
                return True
        except ValueError:
            return True

        return False

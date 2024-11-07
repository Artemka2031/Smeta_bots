from aiogram.filters import Filter
from aiogram.types import Message


class CheckAmount(Filter):
    def __init__(self, amount: str) -> None:
        self.amount = amount

    async def __call__(self, message: Message) -> bool:
        self.amount = message.text

        if ',' in self.amount:
            try:
                # Проверка, что число больше нуля
                return not (float(self.amount.replace(',', '.')) > 0.0)
            except ValueError:
                return True
        elif '.' in self.amount:
            return True  # Встречена точка, возвращаем True
        else:
            try:
                # Проверка, что число больше нуля
                return not (float(self.amount) > 0.0)
            except ValueError:
                return True  # Встречены буквы или другие символы, возвращаем True

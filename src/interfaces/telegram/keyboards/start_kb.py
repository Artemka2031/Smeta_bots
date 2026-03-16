from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_start_kb():
    start_kb = ReplyKeyboardBuilder()
    start_kb.button(text="Расход ₽")
    start_kb.button(text="Приход ₽")
    start_kb.adjust(2)

    return start_kb.as_markup(resize_keyboard=True)

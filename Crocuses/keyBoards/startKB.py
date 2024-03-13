from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_start_kb():
    start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    expence_button = KeyboardButton("Расход 💲")
    comming_button = KeyboardButton("Приход 💲")
    debt_button = KeyboardButton("Долг")

    return start_kb.row(expence_button, comming_button)

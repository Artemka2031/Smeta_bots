from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancle_button = KeyboardButton("Отмена")

start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

start_kb.row(cancle_button)

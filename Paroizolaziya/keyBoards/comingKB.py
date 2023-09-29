from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from Paroizolaziya.keyBoards.generalKB import create_markup_rows

def create_comming_types_kb(types) -> InlineKeyboardMarkup: 
    types_of_expence_kb = InlineKeyboardMarkup() 
    buttons = [(InlineKeyboardButton(i, callback_data=i)) for i in types] 

    rows = create_markup_rows(buttons)

    [types_of_expence_kb.row(*row) for row in rows]

    return types_of_expence_kb
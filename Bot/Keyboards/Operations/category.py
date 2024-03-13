from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database.Tables.ExpensesTables import ExpenseCategory
from Database.Tables.ComingTables import ComingCategory


class TodayCallback(CallbackData, prefix="TDC"):
    today: str



class ChooseCategoryCallback(CallbackData, prefix="CCC"):
    category_id: int
    category_name: str


def category_choose_kb(OperationCategory: ExpenseCategory | ComingCategory):
    choose_category_b = InlineKeyboardBuilder()

    categories = OperationCategory.get_all()

    for category_dic in categories:
        category_id = int(category_dic["id"])
        category_name = category_dic["name"]

        choose_category_b.button(text=category_name,
                                 callback_data=ChooseCategoryCallback(category_id=category_id,
                                                                      category_name=category_name).pack())
    choose_category_b.adjust(2)

    return choose_category_b.as_markup()


def create_today_kb():
    today = datetime.today().strftime('%d.%m.%y')
    text = "Сегодня"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=TodayCallback(today=today).pack())
    return builder.as_markup()

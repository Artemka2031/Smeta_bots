from aiogram.filters.callback_data import CallbackData
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database.Tables.ComingTables import ComingType
from Database.Tables.ExpensesTables import ExpenseType


class ChooseTypeCallback(CallbackData, prefix="CTC"):
    category_id: int
    category_name: str
    type_id: int
    type_name: str


class BackToCategoriesCallback(CallbackData, prefix="BCC"):
    back: bool


class ExpemseType:
    pass


def create_type_kb(category_id, OperationType: ComingType | ExpemseType):
    choose_type_b = InlineKeyboardBuilder()

    category_types = OperationType.get_all_types(category_id)

    for type_dic in category_types:
        category_id = int(type_dic["category_id"])
        category_name = type_dic["category_name"]

        type_id = int(type_dic["type_id"])
        type_name = type_dic["type_name"]

        choose_type_b.button(text=type_name,
                             callback_data=ChooseTypeCallback(category_id=category_id,
                                                              category_name=category_name,
                                                              type_id=type_id,
                                                              type_name=type_name).pack())
    choose_type_b.adjust(2)

    back_button = InlineKeyboardButton(text="Категории",
                                       callback_data=BackToCategoriesCallback(back=True).pack())
    choose_type_b.row(back_button)
    return choose_type_b.as_markup()

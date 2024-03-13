from aiogram.filters.callback_data import CallbackData
from aiogram.types import inline_keyboard_button as ik
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database.Tables.ComingTables import ComingCategory
from Database.Tables.ExpensesTables import ExpenseCategory


class ChooseCategoryEditCallback(CallbackData, prefix="Choose C"):
    category_id: int
    category_name: str
    operation: str


class NewCategoryCallback(CallbackData, prefix="New C"):
    create: bool
    operation: str


def create_category_choose_kb(OperationCategory: ComingCategory | ExpenseCategory, category_create: bool = True):
    chooseCategoryB = InlineKeyboardBuilder()

    categories = OperationCategory.get_all()

    operation = "coming" if OperationCategory == ComingCategory else "expense"

    for category_dic in categories:
        category_id = int(category_dic["id"])
        category_name = category_dic["name"]

        chooseCategoryB.button(text=category_name,
                               callback_data=ChooseCategoryEditCallback(category_id=category_id,
                                                                        category_name=category_name,
                                                                        operation=operation).pack())
    chooseCategoryB.adjust(2)

    if category_create:
        chooseCategoryB.row(ik.InlineKeyboardButton(text="Новая категория",
                                                    callback_data=NewCategoryCallback(create=True,
                                                                                      operation=operation).pack()))
    else:
        chooseCategoryB.row(ik.InlineKeyboardButton(text="Отменить",
                                                    callback_data=NewCategoryCallback(create=False,
                                                                                      operation=operation).pack()))

    return chooseCategoryB.as_markup()

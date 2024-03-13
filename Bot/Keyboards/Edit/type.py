from aiogram.filters.callback_data import CallbackData
from aiogram.types import inline_keyboard_button as ik
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database.Tables.ExpensesTables import ExpenseType, ExpenseCategory
from Database.Tables.ComingTables import ComingType, ComingCategory


class BaseTypeCallbackData(CallbackData, prefix="Base T Callback"):
    category_id: int
    category_name: str
    type_id: int
    type_name: str
    operation: str


class BaseCategoryCallbackData(CallbackData, prefix="Base C Callback"):
    category_id: int
    category_name: str
    operation: str


class ChooseTypeEditCallback(BaseTypeCallbackData, prefix="Choose T"):
    pass


class NewTypeCallback(CallbackData, prefix="New T"):
    category_id: int
    create: bool
    operation: str


class BackToCategoriesEditCallback(CallbackData, prefix="Back to C"):
    back: bool
    operation: str


class RenameCategoryCallback(BaseCategoryCallbackData, prefix="Rename C"):
    pass


class CancelCategoryRenameCallback(BaseCategoryCallbackData, prefix="Cansel Rename C"):
    cancel_rename_category: bool


class DeleteCategoryCallback(BaseCategoryCallbackData, prefix="Delete C"):
    pass


class CancelCategoryDeleteCallback(CallbackData, prefix="Cancel Delete C"):
    cancel_delete_category: bool
    operation: str


def create_type_choose_kb(category_id: int, OperationType: ExpenseType | ComingType,
                          OperationCategory: ExpenseCategory | ComingCategory,
                          create: bool = True, rename_category: bool = False, delete_category: bool = False):
    chooseTypeB = InlineKeyboardBuilder()

    types = OperationType.get_all_types(category_id)
    category_name = OperationCategory.get_name_by_id(category_id)

    operation = "coming" if OperationCategory == ComingCategory else "expense"

    for type_dic in types:
        category_id = int(type_dic["category_id"])
        category_name = type_dic["category_name"]

        type_id = int(type_dic["type_id"])
        type_name = type_dic["type_name"]

        chooseTypeB.button(text=type_name,
                           callback_data=ChooseTypeEditCallback(category_id=category_id,
                                                                category_name=category_name,
                                                                type_id=type_id,
                                                                type_name=type_name, operation=operation).pack())
    chooseTypeB.adjust(2)

    back_button = ik.InlineKeyboardButton(text="Категории",
                                          callback_data=BackToCategoriesEditCallback(back=True,
                                                                                     operation=operation).pack())

    if create:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Новый тип",
                                                callback_data=NewTypeCallback(category_id=category_id,
                                                                              create=True, operation=operation).pack()),
                        back_button
                        )
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Отменить",
                                                callback_data=NewTypeCallback(category_id=category_id,
                                                                              create=False,
                                                                              operation=operation).pack()),
                        back_button
                        )

    if not rename_category:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Переименовать категорию",
                                                callback_data=RenameCategoryCallback(category_id=category_id,
                                                                                     category_name=category_name,
                                                                                     operation=operation).pack()))
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Отмена",
                                                callback_data=CancelCategoryRenameCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_rename_category=True,
                                                                                           operation=operation)
                                                .pack()))

    if not delete_category:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Удалить категорию",
                                                callback_data=DeleteCategoryCallback(category_id=category_id,
                                                                                     category_name=category_name,
                                                                                     operation=operation).pack()))
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Удалить",
                                                callback_data=CancelCategoryDeleteCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_delete_category=False,
                                                                                           operation=operation)
                                                .pack()),
                        ik.InlineKeyboardButton(text="Отмена",
                                                callback_data=CancelCategoryDeleteCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_delete_category=True,
                                                                                           operation=operation)
                                                .pack()))

    return chooseTypeB.as_markup()


class BackToTypesCallback(CallbackData, prefix="Back to T"):
    category_id: int
    back: bool
    operation: str


class RenameTypeCallback(BaseTypeCallbackData, prefix="Rename T"):
    pass


class CancelTypeRenameCallback(CallbackData, prefix="Cansel Rename T"):
    cancel: bool
    operation: str


class DeleteTypeCallback(BaseTypeCallbackData, prefix="Delete type"):
    pass


class CancelTypeDeleteCallback(CallbackData, prefix="Cansel Rename T"):
    cancel_delete: bool
    operation: str


class MoveTypeCallback(BaseTypeCallbackData, prefix="Move type", ):
    pass


def create_edit_type_kb(category_id: int, type_id: int, OperationType: ExpenseType | ComingType,
                        action: str = "Default"):
    type_expense = OperationType.get_type(category_id, type_id)

    operation = "coming" if OperationType == ComingType else "expense"

    category_id = int(type_expense["category_id"])
    category_name = type_expense["category_name"]
    type_id = int(type_expense["type_id"])
    type_name = type_expense["type_name"]

    editTypeB = InlineKeyboardBuilder()

    def create_button(CallbackClass, button_text):
        editTypeB.button(text=button_text,
                         callback_data=CallbackClass(category_id=category_id,
                                                     category_name=category_name,
                                                     type_id=type_id,
                                                     type_name=type_name, operation=operation).pack())

    if action == RenameTypeCallback.__prefix__:
        editTypeB.button(text="Отмена",
                         callback_data=CancelTypeRenameCallback(cancel=True, operation=operation).pack())
    elif action == DeleteTypeCallback.__prefix__:
        editTypeB.button(text="Удалить тип",
                         callback_data=CancelTypeDeleteCallback(cancel_delete=False, operation=operation).pack())
        editTypeB.button(text="Отмена",
                         callback_data=CancelTypeDeleteCallback(cancel_delete=True, operation=operation).pack())
    else:
        create_button(RenameTypeCallback, "Переименовать")
        create_button(DeleteTypeCallback, "Удалить тип")
        # create_button(MoveTypeCallback, "Переместить")

        editTypeB.button(text="Типы",
                         callback_data=BackToTypesCallback(category_id=category_id, back=True,
                                                           operation=operation).pack())

    editTypeB.adjust(2)

    return editTypeB.as_markup()

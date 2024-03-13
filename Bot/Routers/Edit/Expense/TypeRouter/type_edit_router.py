from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Keyboards.Edit.type import (
    BackToCategoriesEditCallback,
    BackToTypesCallback,
    ChooseTypeEditCallback,
    create_edit_type_kb,
    create_type_choose_kb
)
from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType


def create_type_edit_router():
    type_edit_router = Router()

    @type_edit_router.callback_query(ChooseTypeEditCallback.filter(F.operation == "expense"),
                                     flags={"delete_sent_message": True})
    async def edit_type_callback(query: CallbackQuery, callback_data: ChooseTypeEditCallback, state: FSMContext):
        await query.answer()

        category_id = callback_data.category_id
        type_id = callback_data.type_id

        category_name = callback_data.category_name
        type_name = callback_data.type_name

        await query.message.edit_text(text=f'Выберите действие по изменению типа \n'
                                           f'"{type_name}" в категории "{category_name}":',
                                      reply_markup=create_edit_type_kb(category_id, type_id, ExpenseType))

    @type_edit_router.callback_query(BackToTypesCallback.filter((F.back == True) and F.operation == "expense"),
                                     flags={"delete_sent_message": True})
    async def back_to_types_callback(query: CallbackQuery, callback_data: BackToTypesCallback):
        await query.answer()

        category_id = callback_data.category_id
        category_name = ExpenseCategory.get_name_by_id(category_id)

        await query.message.edit_text(text=f'Выберите тип для изменения \nв категории: "{category_name}"',
                                      reply_markup=create_type_choose_kb(category_id=category_id,
                                                                         OperationType=ExpenseType,
                                                                         OperationCategory=ExpenseCategory,
                                                                         create=True))

    @type_edit_router.callback_query(
        BackToCategoriesEditCallback.filter((F.back == True) and (F.operation == "expense")),
        flags={"delete_sent_message": True})
    async def back_to_categories_callback(query: CallbackQuery):
        await query.answer()

        await query.message.edit_text(text=f"Выберите категория для изменения",
                                      reply_markup=create_category_choose_kb(OperationCategory=ExpenseCategory,
                                                                             category_create=True))

    # Создание и включение вложенных роутеров
    from .Type_routers import create_delete_type_router, create_rename_type_router, create_new_type_router
    delete_type_router = create_delete_type_router()
    rename_type_router = create_rename_type_router()
    new_type_router = create_new_type_router()

    type_edit_router.include_router(rename_type_router)
    type_edit_router.include_router(delete_type_router)
    type_edit_router.include_router(new_type_router)

    return type_edit_router

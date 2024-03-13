from aiogram import Router
from aiogram.types import CallbackQuery
from magic_filter import F

from Bot.Keyboards.Edit.category import ChooseCategoryEditCallback
from Bot.Keyboards.Edit.type import create_type_choose_kb
from Database.Tables.ExpensesTables import ExpenseType, ExpenseCategory


def create_category_edit_router():
    category_edit_router = Router()

    @category_edit_router.callback_query(ChooseCategoryEditCallback.filter(F.operation == "expense"),
                                         flags={"delete_sent_message": True})
    async def edit_category_callback(query: CallbackQuery, callback_data: ChooseCategoryEditCallback):
        await query.answer()

        category_id = callback_data.category_id
        category_name = callback_data.category_name

        await query.message.edit_text(text=f'Выберите тип для изменения \nв категории "{category_name}":',
                                      reply_markup=create_type_choose_kb(category_id, OperationType=ExpenseType,
                                                                         OperationCategory=ExpenseCategory))

    # Создание и включение вложенных роутеров
    from .Category_routers import create_delete_category_router, create_new_category_router, \
        create_rename_category_router
    delete_category_router = create_delete_category_router()
    new_category_router = create_new_category_router()
    rename_category_router = create_rename_category_router()

    category_edit_router.include_router(rename_category_router)
    category_edit_router.include_router(delete_category_router)
    category_edit_router.include_router(new_category_router)

    return category_edit_router

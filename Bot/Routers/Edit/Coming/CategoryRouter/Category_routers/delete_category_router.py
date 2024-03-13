from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from Database.Tables.ComingTables import ComingCategory, ComingType
from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Keyboards.Edit.type import DeleteCategoryCallback, CancelCategoryDeleteCallback, create_type_choose_kb

deleteCategoryRouter = Router()


# Удаление категории
class DeleteCategoryComing(StatesGroup):
    query_message = State()
    category_id = State()
    category_name = State()
    confirm = State()


@deleteCategoryRouter.callback_query(DeleteCategoryCallback.filter(F.operation == "coming"),
                                     flags={"delete_sent_message": True})
async def delete_category_action(query: CallbackQuery, callback_data: DeleteCategoryCallback, state: FSMContext):
    await query.answer()

    await state.set_state(DeleteCategoryComing.query_message)

    query_message_id = query.message.message_id
    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_reply_markup(
        reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ComingType,
                                           OperationCategory=ComingCategory,
                                           delete_category=True))

    await state.update_data(query_message=query_message_id, category_id=category_id, category_name=category_name)
    await state.set_state(DeleteCategoryComing.confirm)


@deleteCategoryRouter.callback_query(DeleteCategoryComing.confirm,
                                     CancelCategoryDeleteCallback.filter(F.cancel_delete_category == True))
async def cancel_delete_category_action(query: CallbackQuery, state: FSMContext):
    await query.answer()

    data = (await state.get_data())
    category_id = data["category_id"]

    await state.clear()

    await query.message.edit_reply_markup(
        reply_markup=create_type_choose_kb(category_id, OperationType=ComingType, OperationCategory=ComingCategory))


@deleteCategoryRouter.callback_query(DeleteCategoryComing.confirm,
                                     CancelCategoryDeleteCallback.filter(F.cancel_delete_category == False))
async def delete_category(query: CallbackQuery, state: FSMContext):
    data = (await state.get_data())
    category_id = data["category_id"]
    category_name = data["category_name"]

    await state.clear()

    ComingCategory.delete_category(category_id=category_id)
    await query.answer(text=f'Категория "{category_name}" была удалён')
    await query.message.edit_text(text=f'Выберите категорию для изменения":',
                                  reply_markup=create_category_choose_kb(ComingCategory))

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from Database.Tables.ComingTables import ComingType, ComingCategory
from Bot.Keyboards.Edit.type import DeleteTypeCallback, CancelTypeDeleteCallback, create_edit_type_kb, create_type_choose_kb

deleteTypeRouter = Router()


# Удаление типа
class DeleteComingTypeState(StatesGroup):
    query_message = State()
    category_id = State()
    type_id = State()
    category_name = State()
    type_name = State()
    confirm = State()


@deleteTypeRouter.callback_query(DeleteTypeCallback.filter(F.operation == "coming"))
async def delete_type_action(query: CallbackQuery, callback_data: DeleteTypeCallback, state: FSMContext):
    await query.answer()

    await state.set_state(DeleteComingTypeState.query_message)

    query_message_id = query.message.message_id
    category_id = callback_data.category_id
    type_id = callback_data.type_id
    type_name = callback_data.type_name
    category_name = callback_data.category_name

    await query.message.edit_reply_markup(reply_markup=create_edit_type_kb(category_id=category_id, type_id=type_id,
                                                                           OperationType=ComingType,
                                                                           action=DeleteTypeCallback.__prefix__))

    await state.update_data(query_message=query_message_id, category_id=category_id, type_id=type_id,
                            type_name=type_name, category_name=category_name)
    await state.set_state(DeleteComingTypeState.confirm)


@deleteTypeRouter.callback_query(DeleteComingTypeState.confirm,
                                 CancelTypeDeleteCallback.filter(F.cancel_delete == True))
async def cancel_delete_type_action(query: CallbackQuery, state: FSMContext):
    await query.answer()

    data = (await state.get_data())
    category_id = data["category_id"]
    type_id = data["type_id"]

    await state.clear()

    await query.message.edit_reply_markup(reply_markup=create_edit_type_kb(category_id, type_id, ComingType))


@deleteTypeRouter.callback_query(DeleteComingTypeState.confirm,
                                 CancelTypeDeleteCallback.filter(F.cancel_delete == False))
async def delete_type(query: CallbackQuery, state: FSMContext):
    data = (await state.get_data())
    category_id = data["category_id"]
    category_name = data["category_name"]
    type_id = data["type_id"]
    type_name = data["type_name"]

    await state.clear()

    ComingType.delete_type(type_id)
    await query.answer(text=f'Тип "{type_name}" был удалён из категории "{category_name}"')
    await query.message.edit_text(text=f'Выберите тип для изменения в категории "{category_name}":',
                                  reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ComingType,
                                                                     OperationCategory=ComingCategory))

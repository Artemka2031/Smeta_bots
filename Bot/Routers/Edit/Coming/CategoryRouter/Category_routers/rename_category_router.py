from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import DeleteMessage, EditMessageText
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Database.Tables.ComingTables import ComingCategory, ComingType
from Bot.Keyboards.Edit.type import RenameCategoryCallback, CancelCategoryRenameCallback, create_type_choose_kb
from Bot.Middlewares.Edit.MessageLen import LimitCategoryLenMiddleware

renameCategoryRouter = Router()


# Изменение имени категории
class RenameCategoryComing(StatesGroup):
    query_message = State()
    category_id = State()
    category_name = State()
    sent_message = State()
    new_category_name = State()


@renameCategoryRouter.callback_query(RenameCategoryCallback.filter(F.operation == "coming"),
                                     flags={"delete_sent_message": True})
async def rename_category_action(query: CallbackQuery, callback_data: RenameCategoryCallback, state: FSMContext):
    await query.answer()

    await state.set_state(RenameCategoryComing.query_message)

    query_message_id = query.message.message_id
    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_reply_markup(reply_markup=create_type_choose_kb(
        category_id=category_id, OperationType=ComingType, OperationCategory=ComingCategory,
        rename_category=True))

    message = await query.message.answer(text=f'Переименуйте категорию "{category_name}":')

    await state.update_data(query_message=query_message_id, category_id=category_id,
                            category_name=category_name, sent_message=message.message_id)
    await state.set_state(RenameCategoryComing.new_category_name)


@renameCategoryRouter.callback_query(RenameCategoryComing.new_category_name,
                                     CancelCategoryRenameCallback.filter((F.cancel_rename_category == True)))
async def cancel_rename_category(query: CallbackQuery, state: FSMContext, bot: Bot):
    await query.answer()
    chat_id = query.message.chat.id

    data = (await state.get_data())
    category_id = data["category_id"]
    sent_message = data["sent_message"]

    await state.clear()

    await query.message.edit_reply_markup(
        reply_markup=create_type_choose_kb(category_id, OperationType=ComingType, OperationCategory=ComingCategory,
                                           rename_category=False))
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))


renameCategoryRouter.message.middleware(LimitCategoryLenMiddleware())


@renameCategoryRouter.message(RenameCategoryComing.new_category_name, flags={"limit_category_len": True})
async def rename_category(message: Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id

    data = await state.get_data()
    new_category_name = message.text

    category_id = data["category_id"]

    category_name = data["category_name"]

    query_message = data["query_message"]
    sent_message = data["sent_message"]

    await state.clear()

    await message.delete()
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))

    try:
        ComingCategory.change_category_name(category_id, new_category_name)
        await bot(EditMessageText(chat_id=chat_id, message_id=query_message,
                                  text=f'Выберите тип для изменения \nв категории: "{new_category_name}":',
                                  reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ComingType,
                                                                     OperationCategory=ComingCategory,
                                                                     rename_category=False)))
    except IntegrityError:
        await message.answer(text=f'Тип "{new_category_name}" уже есть в бахе данных')
        await bot(EditMessageText(chat_id=chat_id, message_id=query_message,
                                  text=f'Выберите тип для изменения \nв категории: "{category_name}":',
                                  reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ComingType,
                                                                     OperationCategory=ComingCategory,
                                                                     rename_category=True)))

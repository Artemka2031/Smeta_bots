from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import DeleteMessage, EditMessageReplyMarkup
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Database.Tables.ComingTables import ComingCategory
from Bot.Keyboards.Edit.category import NewCategoryCallback, create_category_choose_kb
from Bot.Middlewares.Edit.MessageLen import LimitCategoryLenMiddleware

newCategoryRouter = Router()


# Новые категории
class NewCategoryComing(StatesGroup):
    query_message = State()
    sent_message = State()
    category_name = State()


@newCategoryRouter.callback_query(NewCategoryCallback.filter((F.create == True) and (F.operation == "coming")))
async def new_category_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(NewCategoryComing.query_message)

    await query.message.edit_reply_markup(
        reply_markup=create_category_choose_kb(OperationCategory=ComingCategory, category_create=False))

    query_message_id = query.message.message_id
    await state.set_state(NewCategoryComing.query_message)
    await state.update_data(query_message=query_message_id)

    message = await query.message.answer(text=f"Напишите название новой категории:")
    await state.set_state(NewCategoryComing.sent_message)
    await state.update_data(sent_message=message.message_id)

    await state.set_state(NewCategoryComing.category_name)


@newCategoryRouter.callback_query(NewCategoryComing.category_name, NewCategoryCallback.filter(F.create == False))
async def cancel_new_category_callback(query: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = query.message.chat.id
    sent_message = (await state.get_data())["sent_message"]

    await query.answer()
    await state.clear()

    await query.message.edit_text(text="Выберите категория для изменения:",
                                  reply_markup=create_category_choose_kb(OperationCategory=ComingCategory,
                                                                         category_create=True))
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))


newCategoryRouter.message.middleware(LimitCategoryLenMiddleware())


@newCategoryRouter.message(NewCategoryComing.category_name, flags={"limit_category_len": True})
async def add_new_category(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(category_name=message.text)

    chat_id = message.chat.id
    message_id = message.message_id
    category_name = message.text

    data = await state.get_data()
    sent_message_id = data['sent_message']
    query_message_id = data['query_message']

    await state.clear()

    try:
        ComingCategory.add(category_name)
    except IntegrityError:
        await message.answer(text=f"Категория с именем '{category_name}' уже существует в базе данных.")

    await bot(EditMessageReplyMarkup(chat_id=chat_id,
                                     message_id=query_message_id,
                                     reply_markup=create_category_choose_kb(ComingCategory)))
    await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message_id))

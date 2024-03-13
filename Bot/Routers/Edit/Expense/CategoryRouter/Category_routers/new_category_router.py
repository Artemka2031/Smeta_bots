from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Bot.Keyboards.Edit.category import NewCategoryCallback, create_category_choose_kb
from Bot.Middlewares.Edit.MessageLen import LimitCategoryLenMiddleware
from Database.Tables.ExpensesTables import ExpenseCategory


def create_new_category_router():
    new_category_router = Router()

    class NewCategoryExpense(StatesGroup):
        query_message = State()
        sent_message = State()
        category_name = State()

    @new_category_router.callback_query(NewCategoryCallback.filter((F.create == True) and (F.operation == "expense")))
    async def new_category_callback(query: CallbackQuery, state: FSMContext):
        await query.answer()
        await state.set_state(NewCategoryExpense.query_message)

        query_message_id = query.message.message_id
        await state.update_data(query_message=query_message_id)

        message = await query.message.answer(text=f"Напишите название новой категории:")
        await state.set_state(NewCategoryExpense.sent_message)
        await state.update_data(sent_message=message.message_id)

        await state.set_state(NewCategoryExpense.category_name)

    @new_category_router.callback_query(NewCategoryExpense.category_name, NewCategoryCallback.filter(F.create == False))
    async def cancel_new_category_callback(query: CallbackQuery, state: FSMContext, bot: Bot):
        chat_id = query.message.chat.id
        sent_message = (await state.get_data())["sent_message"]

        await query.answer()
        await state.clear()

        await query.message.edit_text(text="Выберите категорию для изменения:",
                                      reply_markup=create_category_choose_kb(OperationCategory=ExpenseCategory,
                                                                             category_create=True))
        await bot.delete_message(chat_id=chat_id, message_id=sent_message)

    new_category_router.message.middleware(LimitCategoryLenMiddleware())

    @new_category_router.message(NewCategoryExpense.category_name, flags={"limit_category_len": True})
    async def add_new_category(message: Message, state: FSMContext, bot: Bot):
        chat_id = message.chat.id
        category_name = message.text

        data = await state.get_data()
        sent_message_id = data['sent_message']
        query_message_id = data['query_message']

        await state.clear()

        try:
            ExpenseCategory.add(category_name)
        except IntegrityError:
            await message.answer(text=f"Категория с именем '{category_name}' уже существует в базе данных.")

        await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=query_message_id,
                                            reply_markup=create_category_choose_kb(ExpenseCategory))
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await bot.delete_message(chat_id=chat_id, message_id=sent_message_id)

    return new_category_router

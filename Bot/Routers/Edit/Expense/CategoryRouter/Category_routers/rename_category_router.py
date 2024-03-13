from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Keyboards.Edit.type import RenameCategoryCallback, CancelCategoryRenameCallback, create_type_choose_kb
from Bot.Middlewares.Edit.MessageLen import LimitCategoryLenMiddleware
from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType


def create_rename_category_router():
    rename_category_router = Router()

    class RenameCategoryExpense(StatesGroup):
        query_message = State()
        category_id = State()
        category_name = State()
        sent_message = State()
        new_category_name = State()

    @rename_category_router.callback_query(RenameCategoryCallback.filter(F.operation == "expense"),
                                           flags={"delete_sent_message": True})
    async def rename_category_action(query: CallbackQuery, callback_data: RenameCategoryCallback, state: FSMContext):
        await query.answer()

        query_message_id = query.message.message_id
        category_id = callback_data.category_id
        category_name = callback_data.category_name

        await query.message.edit_reply_markup(reply_markup=create_type_choose_kb(
            category_id=category_id, OperationType=ExpenseType, OperationCategory=ExpenseCategory,
            rename_category=True))

        message = await query.message.answer(text=f'Переименуйте категорию "{category_name}":')

        await state.update_data(query_message=query_message_id, category_id=category_id,
                                category_name=category_name, sent_message=message.message_id)
        await state.set_state(RenameCategoryExpense.new_category_name)

    @rename_category_router.callback_query(RenameCategoryExpense.new_category_name,
                                           CancelCategoryRenameCallback.filter((F.cancel_rename_category == True)))
    async def cancel_rename_category(query: CallbackQuery, state: FSMContext, bot: Bot):
        await query.answer()
        chat_id = query.message.chat.id

        data = (await state.get_data())
        sent_message = data["sent_message"]

        await state.clear()

        await query.message.edit_text("Выберите категорию для изменения:",
                                      reply_markup=create_category_choose_kb(ExpenseCategory, category_create=True))
        await bot.delete_message(chat_id=chat_id, message_id=sent_message)

    rename_category_router.message.middleware(LimitCategoryLenMiddleware())

    @rename_category_router.message(RenameCategoryExpense.new_category_name, flags={"limit_category_len": True})
    async def rename_category(message: Message, state: FSMContext, bot: Bot):
        chat_id = message.chat.id

        data = (await state.get_data())
        new_category_name = message.text
        category_id = data["category_id"]
        query_message = data["query_message"]
        sent_message = data["sent_message"]

        await state.clear()

        await message.delete()
        await bot.delete_message(chat_id=chat_id, message_id=sent_message)

        try:
            ExpenseCategory.change_category_name(category_id, new_category_name)
            await bot.edit_message_text(chat_id=chat_id, message_id=query_message,
                                        text=f'Категория переименована в "{new_category_name}". Выберите тип для изменения:',
                                        reply_markup=create_type_choose_kb(category_id=category_id,
                                                                           OperationType=ExpenseType,
                                                                           OperationCategory=ExpenseCategory,
                                                                           rename_category=False))
        except IntegrityError:
            await message.answer(text=f'Категория с именем "{new_category_name}" уже существует.')
            await bot.edit_message_text(chat_id=chat_id, message_id=query_message,
                                        text=f'Выберите тип для изменения \nв категории: "{category_id}":',
                                        reply_markup=create_type_choose_kb(category_id=category_id,
                                                                           OperationType=ExpenseType,
                                                                           OperationCategory=ExpenseCategory,
                                                                           rename_category=False))

    return rename_category_router

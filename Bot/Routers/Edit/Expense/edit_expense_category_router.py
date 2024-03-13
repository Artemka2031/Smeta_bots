from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Middlewares.Edit.ClearStateMiddleware import ClearStateMiddleware
from Bot.commands import bot_commands
from Database.Tables.ExpensesTables import ExpenseCategory


def create_edit_expense_categories_router():
    edit_expense_categories_router = Router()

    @edit_expense_categories_router.message(Command(bot_commands.edit_expenses))
    @edit_expense_categories_router.message(F.text.casefold() == "редактирование категорий")
    async def start_messaging(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(text="Выберите категорию для изменения",
                             reply_markup=create_category_choose_kb(OperationCategory=ExpenseCategory,
                                                                    category_create=True))

    edit_expense_categories_router.callback_query.middleware(ClearStateMiddleware())

    # Создание вложенных роутеров
    from .CategoryRouter import create_category_edit_router
    from .TypeRouter import create_type_edit_router
    category_edit_router = create_category_edit_router()
    type_edit_router = create_type_edit_router()

    edit_expense_categories_router.include_router(category_edit_router)
    edit_expense_categories_router.include_router(type_edit_router)

    return edit_expense_categories_router

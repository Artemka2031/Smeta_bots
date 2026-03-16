from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.interfaces.telegram.keyboards.operations.category import create_today_kb
from src.interfaces.telegram.routers.add_expense.steps.amount_router import create_amount_router
from src.interfaces.telegram.routers.add_expense.steps.category_router import create_category_router
from src.interfaces.telegram.routers.add_expense.steps.comment_router import create_comment_router
from src.interfaces.telegram.routers.add_expense.steps.date_router import create_date_router
from src.interfaces.telegram.routers.add_expense.steps.wallet_router import create_wallet_router
from src.interfaces.telegram.routers.add_expense.expense_state_class import Expense
from src.interfaces.telegram.commands import bot_commands
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.use_cases import GetProjectCatalog
from src.interfaces.telegram.flow_utils import cancel_operation_flow


def create_expenses_router(bot: ProjectBot):
    expenses_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    @expenses_router.message(Command(bot_commands.add_expense))
    @expenses_router.message(F.text.casefold() == "расход ₽")
    async def start_expense_adding(message: Message, state: FSMContext) -> None:
        # Очищаем текущее состояние
        await state.clear()

        await project_catalog.preload()

        sent_message = await message.answer(
            text="Выберете дату расхода:",
            reply_markup=create_today_kb()
        )

        await state.update_data(date_message_id=sent_message.message_id)
        await state.set_state(Expense.date)

    @expenses_router.message(Command("cancel_expense"))
    @expenses_router.message(F.text.casefold() == "отмена расхода")
    async def delete_expense_adding(message: Message, state: FSMContext) -> None:
        await cancel_operation_flow(
            bot,
            message,
            state,
            tracked_fields=["date_message_id", "chapter_message_id", "amount_message_id", "comment_message_id"],
            cancel_text="Расход отменён",
        )

    expenses_router.include_router(create_date_router(bot))
    expenses_router.include_router(create_wallet_router(bot))
    expenses_router.include_router(create_category_router(bot))
    expenses_router.include_router(create_amount_router(bot))
    expenses_router.include_router(create_comment_router(bot))

    return expenses_router

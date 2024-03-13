from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message

from Bot.Keyboards.Operations.category import create_today_kb
from Bot.Routers.AddExpense.ExpenseRouter.amount_router import create_amount_router
from Bot.Routers.AddExpense.ExpenseRouter.category_router import create_category_router
from Bot.Routers.AddExpense.ExpenseRouter.comment_router import create_comment_router
from Bot.Routers.AddExpense.ExpenseRouter.date_router import create_date_router
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.commands import bot_commands


def create_expenses_router(bot: Bot):
    expenses_router = Router()

    @expenses_router.message(Command(bot_commands.add_expense))
    @expenses_router.message(F.text.casefold() == "расход")
    async def start_expense_adding(message: Message, state: FSMContext) -> None:
        await state.clear()
        sent_message = await message.answer(text="Выберете дату расхода:",
                                            reply_markup=create_today_kb())
        await state.update_data(date_message_id=sent_message.message_id)
        await state.set_state(Expense.date)

    @expenses_router.message(Command("cancel_expense"))
    @expenses_router.message(F.text.casefold() == "отмена расхода")
    async def delete_expense_adding(message: Message, state: FSMContext) -> None:
        chat_id = message.chat.id
        data = await state.get_data()
        await message.delete()

        fields_to_check = ["date_message_id", "category_message_id", "amount_message_id", "comment_message_id"]

        delete_messages = [data[field] for field in fields_to_check if field in data]

        extra_messages = data.get("extra_messages", [])
        delete_messages.extend(extra_messages)

        for message_id in delete_messages:
            await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))

        await message.answer(text="Расход отменён")
        await state.clear()

    # Добавляем роутеры по работе с датой, категориями, суммой расхода и комментариями
    expenses_router.include_router(create_date_router(bot))
    expenses_router.include_router(create_category_router())
    expenses_router.include_router(create_amount_router(bot))
    expenses_router.include_router(create_comment_router(bot))

    return expenses_router

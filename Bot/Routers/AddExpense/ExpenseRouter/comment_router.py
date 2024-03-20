from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot.Keyboards.Operations.delete import create_delete_operation_kb, DeleteOperation, ConfirmDeleteOperation
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.create_bot import ProjectBot
from Database.Tables.ExpensesTables import Expense as ExpenseDB


def create_comment_router(bot: ProjectBot):
    comment_router = Router()

    @comment_router.message(Expense.comment)
    async def set_comment(message: Message, state: FSMContext):
        await message.delete()
        chat_id = message.chat.id
        comment = message.text
        data = await state.get_data()

        date = data["date"]
        category_id = data["category"]["category_id"]
        category_name = data["category"]["category_name"]
        type_id = data["type"]["type_id"]
        type_name = data["type"]["type_name"]
        amount = data["amount"]

        expense = ExpenseDB.add(date, category_id, type_id, amount, comment)
        expense_id = expense.id

        messages_ids = [data["date_message_id"], data["category_message_id"],
                        data["amount_message_id"], data["comment_message_id"]]

        await state.clear()

        for message_id in messages_ids:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)

        await bot.send_message(chat_id=chat_id,
                               text=f"<b>✨ Добавлен расход</b>\n"
                                    f"Дата: <code>{date}</code>\n"
                                    f"Тип: <code>{type_name}</code>\n"
                                    f"Категория: <code>{category_name}</code>\n"
                                    f"Сумма: <code>{amount}</code>\n"
                                    f"Комментарий: <code>{comment}</code>\n",
                               reply_markup=create_delete_operation_kb(operation_id=expense_id, confirm=False))

    @comment_router.callback_query(DeleteOperation.filter(F.delete == True))
    async def confirm_delete_expense(query: CallbackQuery, callback_data: DeleteOperation):
        await query.answer()
        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(reply_markup=create_delete_operation_kb(expense_id, True))

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == True))
    async def delete_expense(query: CallbackQuery, callback_data: DeleteOperation):
        await query.answer()

        message_text = query.message.text
        expense_id = callback_data.operation_id

        try:
            ExpenseDB.remove(expense_id)
            await query.message.edit_text(text="<b>***Удалено***</b>\n" + message_text, reply_markup=None)
        except ExpenseDB.DoesNotExist:
            await query.message.answer(text="Расход не найден")
        except Exception as e:
            await query.message.answer(text=f"Неизвестная ошибка: {e}")

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
        await query.answer()

        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(
            reply_markup=create_delete_operation_kb(operation_id=expense_id, confirm=False))

    return comment_router

from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot.Keyboards.Operations.delete import create_delete_operation_kb, DeleteOperation, ConfirmDeleteOperation
from Bot.Keyboards.start_kb import create_start_kb
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.create_bot import ProjectBot


def create_comment_router(bot: ProjectBot):
    comment_router = Router()

    @comment_router.message(Expense.comment)
    async def set_comment(message: Message, state: FSMContext):
        await message.delete()
        comment = message.text

        data = await state.get_data()

        await state.clear()

        comment_message_id = data["comment_message_id"]
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=comment_message_id,
            text=f"Комментарий: {comment}"
        )

        date_obj = datetime.strptime(data["date"], '%d.%m.%y')
        date = date_obj.strftime('%d.%m.%Y')

        amount = data["amount"]
        wallet = data["wallet"]
        chat_id = message.chat.id

        messages_ids = [
            data["date_message_id"],
            data["wallet_message_id"],
            data["amount_message_id"],
            data["comment_message_id"]
        ]

        if "chapter_message_id" in data:
            messages_ids.append(data["chapter_message_id"])

        try:
            [await bot.delete_message(chat_id=chat_id, message_id=message_id) for message_id in messages_ids]
        except Exception:
            pass

        if wallet == "Проект":
            chapter_code = data["chapter_code"]
            category_code = data.get("category_code", "")
            subcategory_code = data.get("subcategory_code", "")

            processing_message = await bot.send_message(chat_id=chat_id, text="Идет процесс добавления расхода...")

            category_name = bot.google_sheets.get_category_name(chapter_code, category_code)
            subcategory_name = (
                bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code)
                if subcategory_code else ""
            )

            category_name_to_use = subcategory_name or category_name
            category_code_to_use = subcategory_code or category_code

            bot.google_sheets.update_expense_with_comment(chapter_code, category_code_to_use, date, amount, comment)

            operation_id = await bot.record_expense_operation(chapter_code, category_code_to_use, date, amount, comment)

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_message.message_id,
                text=(
                    f"<b>✨ Расход успешно добавлен</b>\n"
                    f"Дата: <code>{date}</code>\n"
                    f"Категория: <code>{category_name_to_use}</code>\n"
                    f"Сумма: <code>{amount}</code> ₽\n"
                    f"Комментарий: <code>{comment}</code>\n"
                ),
                reply_markup=create_delete_operation_kb(operation_id, False)
            )

        elif wallet == "Взять в долг":
            chapter_code = data["chapter_code"]
            category_code = data.get("category_code", "")
            subcategory_code = data.get("subcategory_code", "")
            coefficient = data.get("coefficient", 1.0)  # По умолчанию коэффициент 1

            processing_message = await bot.send_message(chat_id=chat_id,
                                                        text="Идет процесс добавления записи о долге и расходе...")

            category_name = bot.google_sheets.get_category_name(chapter_code, category_code)
            subcategory_name = (
                bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code)
                if subcategory_code else ""
            )
            category_name_to_use = subcategory_name or category_name
            category_code_to_use = subcategory_code or category_code

            creditor = data["creditor"]
            borrowing_amount = round(amount * coefficient, 2)
            saving_amount = round(amount * (1 - coefficient), 2) if coefficient != 1 else 0

            bot.google_sheets.update_expense_with_comment(chapter_code, category_code_to_use, date, borrowing_amount,
                                                          comment)

            bot.google_sheets.record_borrowing(creditor, date, amount, comment)

            operation_id = await bot.record_operation(date, creditor, chapter_code, category_code_to_use, amount,
                                                      coefficient, comment)

            if saving_amount > 0:
                bot.google_sheets.record_saving(creditor, date, saving_amount, comment)

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_message.message_id,
                text=(
                    f"<b>✨ Записан долг и расход</b>\n"
                    f"Дата: <code>{date}</code>\n"
                    f"Категория: <code>{category_name_to_use}</code>\n"
                    f"Кредитор: <code>{creditor}</code>\n"
                    f"Коэффициент: <code>{coefficient}</code>\n"
                    f"Сумма расхода: <code>{borrowing_amount}</code> ₽\n"
                    f"Экономия: <code>{saving_amount}</code> ₽\n"
                    f"Сумма долга: <code>{amount}</code> ₽\n"
                    f"Комментарий: <code>{comment}</code>\n"
                ),
                reply_markup=create_delete_operation_kb(operation_id, False)
            )

        elif wallet == "Вернуть долг":
            creditor = data["creditor"]
            processing_message = await bot.send_message(chat_id=chat_id, text="Идет процесс возврата долга...")

            bot.google_sheets.record_repayment(creditor, date, amount, comment)
            operation_id = await bot.record_debt_repayment(creditor, date, amount, comment)

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_message.message_id,
                text=(
                    f"<b>✨ Возврат долга</b>\n"
                    f"Дата: <code>{date}</code>\n"
                    f"Кредитор: <code>{creditor}</code>\n"
                    f"Сумма: <code>{amount}</code> ₽\n"
                    f"Комментарий: <code>{comment}</code>\n"
                ),
                reply_markup=create_delete_operation_kb(operation_id, False)
            )

        # Завершающее сообщение
        await bot.send_message(chat_id=chat_id, text="Выберите следующую операцию:", reply_markup=create_start_kb())

    # Роутер для удаления операции
    @comment_router.callback_query(DeleteOperation.filter(F.delete == True))
    async def confirm_delete_expense(query: CallbackQuery, callback_data: DeleteOperation):
        await query.answer()
        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(reply_markup=create_delete_operation_kb(expense_id, True))

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == True))
    async def delete_expense(query: CallbackQuery, callback_data: DeleteOperation):
        await query.answer()

        message_text = query.message.text
        await query.message.edit_text(text="Идет процесс удаления записи...\n\n" + message_text, reply_markup=None)

        operation_id = callback_data.operation_id

        expense = await bot.get_expense_by_id(operation_id)

        if expense.creditor and expense.chapter_code:
            bot.google_sheets.remove_expense(expense.chapter_code, expense.category_code_to_use, expense.date,
                                             round(expense.amount * expense.coefficient, 2), expense.comment)
            bot.google_sheets.remove_borrowing(expense.creditor, expense.date, expense.amount, expense.comment)
            if expense.coefficient != 1:
                saving_amount = expense.amount * (1 - expense.coefficient)
                bot.google_sheets.remove_saving(expense.creditor, expense.date, saving_amount, expense.comment)
        elif expense.creditor:
            bot.google_sheets.remove_repayment(expense.creditor, expense.date, expense.amount, expense.comment)
        else:
            bot.google_sheets.remove_expense(expense.chapter_code, expense.category_code_to_use, expense.date,
                                             expense.amount, expense.comment)

        expense.delete_instance()

        await query.message.edit_text("*** Удалено ***\n\n" + message_text)

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
        await query.answer()

        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(
            reply_markup=create_delete_operation_kb(operation_id=expense_id, confirm=False)
        )

    return comment_router

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

        # Загружаем данные из состояния
        data = await state.get_data()

        # Очищаем состояние после получения данных
        await state.clear()

        # Обновляем сообщение с комментарием
        comment_message_id = data["comment_message_id"]
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=comment_message_id,
            text=f"Комментарий: {comment}"
        )

        # Форматируем дату
        date_obj = datetime.strptime(data["date"], '%d.%m.%y')
        date = date_obj.strftime('%d.%m.%Y')

        amount = data["amount"]
        wallet = data["wallet"]
        chat_id = message.chat.id

        codes = data["column_b_values"]
        names = data["column_c_values"]
        dates = data["dates_row"]

        # Собираем ID сообщений, которые нужно удалить
        messages_ids = [
            data["date_message_id"],
            data["wallet_message_id"],
            data["amount_message_id"],
            data["comment_message_id"]
        ]

        if "chapter_message_id" in data:
            messages_ids.append(data["chapter_message_id"])

        # Пытаемся удалить сообщения
        try:
            [await bot.delete_message(chat_id=chat_id, message_id=message_id) for message_id in messages_ids]
        except Exception:
            pass

        # Логика для разных кошельков
        if wallet == "Проект":
            chapter_code = data["chapter_code"]
            category_code = data.get("category_code", "")
            subcategory_code = data.get("subcategory_code", "")

            # Отправляем сообщение о процессе добавления расхода
            processing_message = await bot.send_message(chat_id=chat_id, text="Идет процесс добавления расхода...")

            # Получаем названия категории и подкатегории
            category_name = data.get("category_name",
                                     bot.google_sheets.get_category_name(chapter_code, category_code, codes, names))
            subcategory_name = data.get(
                "subcategory_name",
                bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code, codes, names)
            ) if subcategory_code else ""

            category_name_to_use = subcategory_name or category_name
            category_code_to_use = subcategory_code or category_code

            # Обновляем расход с комментарием в Google Sheets
            bot.google_sheets.update_expense_with_comment(chapter_code, category_code_to_use, date, amount, comment,
                                                          codes, names, dates)

            # Записываем операцию в БД
            operation_id = await bot.record_expense_operation(chapter_code, category_code_to_use, date, amount, comment)

            # Обновляем сообщение с результатом
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
            coefficient = data.get("coefficient", 1.0)

            processing_message = await bot.send_message(chat_id=chat_id,
                                                        text="Идет процесс добавления записи о долге и расходе...")

            # Получаем названия категории и подкатегории
            category_name = data.get("category_name",
                                     bot.google_sheets.get_category_name(chapter_code, category_code, codes, names))
            subcategory_name = data.get(
                "subcategory_name",
                bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code, codes, names)
            ) if subcategory_code else ""

            category_name_to_use = subcategory_name or category_name
            category_code_to_use = subcategory_code or category_code

            creditor = data["creditor"]
            borrowing_amount = round(amount * coefficient, 2)
            saving_amount = round(amount * (1 - coefficient), 2) if coefficient != 1 else 0

            # Обновляем расход и долг в Google Sheets
            bot.google_sheets.update_expense_with_comment(chapter_code, category_code_to_use, date, borrowing_amount,
                                                          comment, codes, names, dates)
            bot.google_sheets.record_borrowing(creditor, date, amount, comment, codes, names, dates)

            # Записываем операцию в БД
            operation_id = await bot.record_operation(date, creditor, chapter_code, category_code_to_use, amount,
                                                      coefficient, comment)

            if saving_amount > 0:
                bot.google_sheets.record_saving(creditor, date, saving_amount, comment, codes, names, dates)

            # Обновляем сообщение с результатом
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

            # Записываем возврат долга в Google Sheets
            bot.google_sheets.record_repayment(creditor, date, amount, comment, codes, names, dates)

            # Записываем операцию возврата долга в БД
            operation_id = await bot.record_debt_repayment(creditor, date, amount, comment)

            # Обновляем сообщение с результатом
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

        # Получаем запись расхода из БД
        expense = await bot.get_expense_by_id(operation_id)

        if expense.creditor and expense.chapter_code:
            # Удаляем расход и долг из Google Sheets
            bot.google_sheets.remove_expense(expense.chapter_code, expense.category_code_to_use, expense.date,
                                             round(expense.amount * expense.coefficient, 2), expense.comment)
            bot.google_sheets.remove_borrowing(expense.creditor, expense.date, expense.amount, expense.comment)

            if expense.coefficient != 1:
                saving_amount = expense.amount * (1 - expense.coefficient)
                bot.google_sheets.remove_saving(expense.creditor, expense.date, saving_amount, expense.comment)
        elif expense.creditor:
            # Удаляем запись возврата долга
            bot.google_sheets.remove_repayment(expense.creditor, expense.date, expense.amount, expense.comment)
        else:
            # Удаляем только расход
            bot.google_sheets.remove_expense(expense.chapter_code, expense.category_code_to_use, expense.date,
                                             expense.amount, expense.comment)

        # Удаляем запись из базы данных
        expense.delete_instance()

        # Обновляем сообщение о том, что запись удалена
        await query.message.edit_text("*** Удалено ***\n\n" + message_text)

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
        await query.answer()

        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(
            reply_markup=create_delete_operation_kb(operation_id=expense_id, confirm=False)
        )

    return comment_router

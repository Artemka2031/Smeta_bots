from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot.Keyboards.Operations.delete import create_delete_operation_kb, create_delete_coming_kb, DeleteComing, \
    ConfirmDeleteComing
from Bot.Keyboards.start_kb import create_start_kb
from Bot.Routers.AddComing.coming_state_class import Coming
from Bot.create_bot import ProjectBot


def create_comment_router(bot: ProjectBot):
    comment_router = Router()

    @comment_router.message(Coming.comment)
    async def set_comment(message: Message, state: FSMContext):
        await message.delete()
        comment = message.text

        data = await state.get_data()
        await state.clear()

        comment_message_id = data["comment_message_id"]
        await bot.edit_message_text(chat_id=message.chat.id, message_id=comment_message_id,
                                    text=f"Комментарий: {comment}")

        date_obj = datetime.strptime(data["date"], '%d.%m.%y')
        date = date_obj.strftime('%d.%m.%Y')

        amount = data["amount"]

        chat_id = message.chat.id

        messages_ids = [data["date_message_id"], data["amount_message_id"],
                        data["comment_message_id"]]

        try:
            chapter_message_id = data["chapter_message_id"]
            messages_ids.append(chapter_message_id)
        except KeyError:
            pass

        try:
            [await bot.delete_message(chat_id=chat_id, message_id=message_id) for message_id in messages_ids]
        except Exception:
            pass

        chapter_code = data["chapter_code"]
        coming_code = data.get("coming_code", "")

        processing_message = await bot.send_message(chat_id=chat_id, text="Идет процесс добавления прихода...")

        bot.google_sheets.update_coming_with_comment(chapter_code, coming_code, date, amount,
                                                           comment)

        operation_id = await bot.record_coming_operation(chapter_code, coming_code, date, amount, comment)

        await bot.edit_message_text(chat_id=chat_id, message_id=processing_message.message_id,
                                    text=f"<b>✨ Расход успешно добавлен</b>\n"
                                         f"Дата: <code>{date}</code>\n"
                                         f"Категория: <code>{'Приходы'}</code>\n"
                                         f"Сумма: <code>{amount}</code> ₽\n"
                                         f"Комментарий: <code>{comment}</code>\n",
                                    reply_markup=create_delete_coming_kb(operation_id, False))

        await bot.send_message(chat_id=chat_id, text="Выберите следующую операцию:", reply_markup=create_start_kb())

    @comment_router.callback_query(DeleteComing.filter(F.delete == True))
    async def confirm_delete_coming(query: CallbackQuery, callback_data: DeleteComing):
        await query.answer()
        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(reply_markup=create_delete_coming_kb(expense_id, True))

    @comment_router.callback_query(ConfirmDeleteComing.filter(F.confirm_delete == True))
    async def delete_coming(query: CallbackQuery, callback_data: ConfirmDeleteComing):
        await query.answer()

        message_text = query.message.text
        await query.message.edit_text(text="Идет процесс удаления прихода...\n\n" + message_text, reply_markup=None)

        operation_id = callback_data.operation_id

        coming = await bot.get_coming_by_id(operation_id)

        bot.google_sheets.remove_coming(coming.chapter_code, coming.coming_code, coming.date,
                                              coming.amount, coming.comment)

        # Удаление записи из базы данных
        coming.delete_instance()

        # Отправка сообщения пользователю об успешном удалении
        await query.message.edit_text("*** Удалено ***\n\n" + message_text)

    @comment_router.callback_query(ConfirmDeleteComing.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteComing):
        await query.answer()

        expense_id = callback_data.operation_id
        await query.message.edit_reply_markup(
            reply_markup=create_delete_operation_kb(operation_id=expense_id, confirm=False))

    return comment_router

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message, CallbackQuery

from Database.Tables.ComingTables import Coming as ComingDB
from Bot.Keyboards.Operations.delete import create_delete_operation_kb, DeleteOperation, ConfirmDeleteOperation
from Bot.Routers.AddComing.coming_state_class import Coming

commentRouter = Router()


@commentRouter.message(Coming.comment)
async def set_comment(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    chat_id = message.chat.id
    comment = message.text
    data = (await state.get_data())

    date = data["date"]
    category_id = data["category"]["category_id"]
    category_name = data["category"]["category_name"]
    type_id = data["type"]["type_id"]
    type_name = data["type"]["type_name"]
    amount = data["amount"]

    coming = ComingDB.add(date, category_id, type_id, amount, comment)
    coming_id = coming.id

    messages_ids = [data["date_message_id"], data["category_message_id"],
                    data["amount_message_id"], data["comment_message_id"]]

    await state.clear()

    try:
        for message_id in messages_ids:
            await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
    except:
        pass

    await message.answer(
        text=(
            f"<b>📥 Новый приход</b>\n\n"
            f"🗓 <b>Дата:</b> <code>{date}</code>\n"
            f"🔖 <b>Тип:</b> <code>{type_name}</code>\n"
            f"📁 <b>Категория:</b> <code>{category_name}</code>\n"
            f"💵 <b>Сумма:</b> <code>{amount}</code> руб.\n"
            f"💬 <b>Комментарий:</b> <code>{comment if comment else 'Нет'}</code>\n"
        ),
        reply_markup=create_delete_operation_kb(operation_id=coming_id, confirm=False),
        parse_mode='HTML'
    )


@commentRouter.callback_query(DeleteOperation.filter(F.delete == True))
async def confirm_delete_coming(query: CallbackQuery, callback_data: DeleteOperation):
    await query.answer()
    coming_id = callback_data.operation_id
    await query.message.edit_reply_markup(reply_markup=create_delete_operation_kb(coming_id, True))


@commentRouter.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == True))
async def delete_coming(query: CallbackQuery, callback_data: DeleteOperation):
    await query.answer()

    message_text = query.message.text
    coming_id = callback_data.operation_id

    try:
        ComingDB.remove(coming_id)
        await query.message.edit_text(text="<b>***Удалено***</b>\n" + message_text, reply_markup=None)
    except ComingDB.DoesNotExist:
        await query.message.answer(text="Расход не найден")
    except:
        await query.message.answer(text=f"Неизвестная ошибка")


@commentRouter.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == False))
async def cancel_delete_coming(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
    await query.answer()

    coming_id = callback_data.operation_id
    await query.message.edit_reply_markup(reply_markup=create_delete_operation_kb(operation_id=coming_id, confirm=False))

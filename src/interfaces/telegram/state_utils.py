from __future__ import annotations

async def clear_extra_messages(bot, state, chat_id: int, logger=None) -> None:
    data = await state.get_data()
    extra_messages = data.get("extra_messages") or []
    for message_id in extra_messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as exc:
            if logger is not None:
                logger.warning(f"Не удалось удалить служебное сообщение {message_id}: {exc}")
    await state.update_data(extra_messages=[])


async def ensure_extra_message(bot, state, chat_id: int, text: str) -> None:
    data = await state.get_data()
    extra_messages = data.get("extra_messages") or []
    if extra_messages:
        return

    message = await bot.send_message(chat_id=chat_id, text=text)
    await state.update_data(extra_messages=[message.message_id])


async def delete_message_ids(
    bot,
    chat_id: int,
    message_ids: list[int],
    logger=None,
) -> None:
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as exc:
            if logger is not None:
                logger.warning(f"Не удалось удалить сообщение {message_id}: {exc}")

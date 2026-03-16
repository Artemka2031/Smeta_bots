from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .error_utils import log_handler_exception, map_exception_to_user_text
from .state_utils import clear_extra_messages, delete_message_ids


async def finalize_comment_input(
    bot,
    state: FSMContext,
    message: Message,
    *,
    tracked_fields: list[str],
) -> tuple[dict[str, Any], str, int]:
    await message.delete()
    comment = message.text
    data = await state.get_data()
    await state.clear()

    chat_id = message.chat.id
    comment_message_id = data["comment_message_id"]
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=comment_message_id,
        text=f"Комментарий: {comment}",
    )

    message_ids = [data[field] for field in tracked_fields if field in data]
    await clear_extra_messages(bot, state, chat_id, bot.logger)
    await delete_message_ids(bot, chat_id, message_ids, bot.logger)
    return data, comment, chat_id


async def execute_create_flow(
    bot,
    *,
    chat_id: int,
    action: str,
    processing_text: str,
    fallback_error_text: str,
    execute: Callable[[], Awaitable[Any]],
    render_success: Callable[[int], str],
    keyboard_factory: Callable[[int], Any],
) -> bool:
    processing_message = await bot.send_message(chat_id=chat_id, text=processing_text)

    try:
        result = await execute()
    except Exception as exc:
        log_handler_exception(bot.logger, action, exc)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_message.message_id,
            text=map_exception_to_user_text(exc, fallback_error_text),
        )
        return False

    operation_id = result.operation_id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=processing_message.message_id,
        text=render_success(operation_id),
        reply_markup=keyboard_factory(operation_id),
    )
    return True


async def toggle_delete_confirmation(
    query: CallbackQuery,
    *,
    operation_id: int,
    keyboard_factory: Callable[[int, bool], Any],
    confirm: bool,
) -> None:
    await query.answer()
    await query.message.edit_reply_markup(reply_markup=keyboard_factory(operation_id, confirm))


async def execute_delete_flow(
    bot,
    query: CallbackQuery,
    *,
    operation_id: int,
    action: str,
    progress_text: str,
    fallback_error_text: str,
    execute: Callable[[], Awaitable[Any]],
) -> None:
    await query.answer()

    message_text = query.message.text
    await query.message.edit_text(text=f"{progress_text}\n\n{message_text}", reply_markup=None)

    try:
        await execute()
    except Exception as exc:
        log_handler_exception(bot.logger, action, exc, operation_id=operation_id)
        await query.message.edit_text(text=map_exception_to_user_text(exc, fallback_error_text))
        return

    await query.message.edit_text(f"*** Удалено ***\n\n{message_text}")

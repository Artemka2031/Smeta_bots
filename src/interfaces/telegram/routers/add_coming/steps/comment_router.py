from decimal import Decimal

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.interfaces.telegram.keyboards.operations.delete import create_delete_coming_kb, DeleteComing, ConfirmDeleteComing
from src.interfaces.telegram.routers.add_coming.coming_state_class import Coming
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.dto import CreateComingCommand
from src.application.use_cases import CreateComingOperation, DeleteProjectOperation
from src.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.interfaces.telegram.date_utils import format_sheet_date, parse_input_date
from src.interfaces.telegram.flow_utils import send_next_operation_prompt
from src.interfaces.telegram.operation_flow import (
    execute_create_flow,
    execute_delete_flow,
    finalize_comment_input,
    toggle_delete_confirmation,
)
from src.interfaces.telegram.operation_messages import render_coming_success


def create_comment_router(bot: ProjectBot):
    comment_router = Router()

    @comment_router.message(Coming.comment)
    async def set_comment(message: Message, state: FSMContext):
        data, comment, chat_id = await finalize_comment_input(
            bot,
            state,
            message,
            tracked_fields=["date_message_id", "chapter_message_id", "amount_message_id", "comment_message_id"],
        )

        operation_date = parse_input_date(data["date"])
        date = format_sheet_date(operation_date)
        amount = data["amount"]
        chapter_code = data["chapter_code"]
        coming_code = data.get("coming_code", "")

        created = await execute_create_flow(
            bot,
            chat_id=chat_id,
            action="create_coming",
            processing_text="Идет процесс добавления прихода...",
            fallback_error_text="Не удалось принять приход. Попробуйте позже.",
            execute=lambda: CreateComingOperation(SqlAlchemyUnitOfWork()).execute(
                CreateComingCommand(
                    project_key=bot.project_key,
                    operation_date=operation_date,
                    amount=Decimal(str(amount)),
                    chapter_code=chapter_code,
                    coming_code=coming_code,
                    comment=comment,
                    mark_synced=False,
                )
            ),
            render_success=lambda operation_id: render_coming_success(date, amount, comment),
            keyboard_factory=lambda operation_id: create_delete_coming_kb(operation_id, False, storage="shared"),
        )
        if not created:
            return

        await send_next_operation_prompt(bot, chat_id)

    @comment_router.callback_query(DeleteComing.filter(F.delete == True))
    async def confirm_delete_coming(query: CallbackQuery, callback_data: DeleteComing):
        await toggle_delete_confirmation(
            query,
            operation_id=callback_data.operation_id,
            keyboard_factory=lambda operation_id, confirm: create_delete_coming_kb(
                operation_id,
                confirm,
                storage="shared",
            ),
            confirm=True,
        )

    @comment_router.callback_query(ConfirmDeleteComing.filter(F.confirm_delete == True))
    async def delete_coming(query: CallbackQuery, callback_data: ConfirmDeleteComing):
        await execute_delete_flow(
            bot,
            query,
            operation_id=callback_data.operation_id,
            action="delete_coming",
            progress_text="Идет процесс удаления прихода...",
            fallback_error_text="Не удалось удалить запись. Попробуйте позже.",
            execute=lambda: DeleteProjectOperation(SqlAlchemyUnitOfWork()).execute(
                project_key=bot.project_key,
                operation_id=callback_data.operation_id,
            ),
        )

    @comment_router.callback_query(ConfirmDeleteComing.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteComing):
        await toggle_delete_confirmation(
            query,
            operation_id=callback_data.operation_id,
            keyboard_factory=lambda operation_id, confirm: create_delete_coming_kb(
                operation_id,
                confirm,
                storage="shared",
            ),
            confirm=False,
        )

    return comment_router

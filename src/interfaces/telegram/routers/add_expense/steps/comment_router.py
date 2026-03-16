from decimal import Decimal

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.interfaces.telegram.keyboards.operations.delete import create_delete_operation_kb, DeleteOperation, ConfirmDeleteOperation
from src.interfaces.telegram.routers.add_expense.expense_state_class import Expense
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.dto import CreateBorrowedExpenseCommand, CreateExpenseCommand, CreateRepaymentCommand
from src.application.use_cases import (
    CreateBorrowedExpenseOperation,
    CreateExpenseOperation,
    CreateRepaymentOperation,
    DeleteProjectOperation,
    GetProjectCatalog,
)
from src.domain.services import calculate_borrowing_breakdown
from src.infrastructure.db.uow import SqlAlchemyUnitOfWork
from src.interfaces.telegram.date_utils import format_sheet_date, parse_input_date
from src.interfaces.telegram.flow_utils import send_next_operation_prompt
from src.interfaces.telegram.operation_flow import (
    execute_create_flow,
    execute_delete_flow,
    finalize_comment_input,
    toggle_delete_confirmation,
)
from src.interfaces.telegram.operation_messages import (
    render_borrowed_expense_success,
    render_expense_success,
    render_repayment_success,
)


def create_comment_router(bot: ProjectBot):
    comment_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    @comment_router.message(Expense.comment)
    async def set_comment(message: Message, state: FSMContext):
        data, comment, chat_id = await finalize_comment_input(
            bot,
            state,
            message,
            tracked_fields=[
                "date_message_id",
                "wallet_message_id",
                "chapter_message_id",
                "amount_message_id",
                "comment_message_id",
            ],
        )
        operation_date = parse_input_date(data["date"])
        date = format_sheet_date(operation_date)
        amount = data["amount"]
        wallet = data["wallet"]

        if wallet == "Проект":
            chapter_code = data["chapter_code"]
            category_code = data.get("category_code", "")
            subcategory_code = data.get("subcategory_code", "")

            category_name = data.get("category_name")
            if category_name is None:
                category_name = await project_catalog.get_category_name(chapter_code, category_code)
            subcategory_name = data.get("subcategory_name")
            if subcategory_code and subcategory_name is None:
                subcategory_name = await project_catalog.get_subcategory_name(
                    chapter_code,
                    category_code,
                    subcategory_code,
                )
            subcategory_name = subcategory_name or ""

            category_name_to_use = subcategory_name or category_name
            created = await execute_create_flow(
                bot,
                chat_id=chat_id,
                action="create_expense",
                processing_text="Идет процесс добавления расхода...",
                fallback_error_text="Не удалось принять расход. Попробуйте позже.",
                execute=lambda: CreateExpenseOperation(SqlAlchemyUnitOfWork()).execute(
                    CreateExpenseCommand(
                        project_key=bot.project_key,
                        operation_date=operation_date,
                        amount=Decimal(str(amount)),
                        chapter_code=chapter_code,
                        category_code=category_code,
                        subcategory_code=subcategory_code or None,
                        comment=comment,
                        mark_synced=False,
                    )
                ),
                render_success=lambda operation_id: render_expense_success(
                    date,
                    category_name_to_use,
                    amount,
                    comment,
                ),
                keyboard_factory=lambda operation_id: create_delete_operation_kb(
                    operation_id,
                    False,
                    storage="shared",
                ),
            )
            if not created:
                return

        elif wallet == "Взять в долг":
            chapter_code = data["chapter_code"]
            category_code = data.get("category_code", "")
            subcategory_code = data.get("subcategory_code", "")
            coefficient = data.get("coefficient", 1.0)

            category_name = data.get("category_name")
            if category_name is None:
                category_name = await project_catalog.get_category_name(chapter_code, category_code)
            subcategory_name = data.get("subcategory_name")
            if subcategory_code and subcategory_name is None:
                subcategory_name = await project_catalog.get_subcategory_name(
                    chapter_code,
                    category_code,
                    subcategory_code,
                )
            subcategory_name = subcategory_name or ""

            category_name_to_use = subcategory_name or category_name
            creditor = data["creditor"]
            breakdown = calculate_borrowing_breakdown(
                Decimal(str(amount)),
                Decimal(str(coefficient)),
            )

            created = await execute_create_flow(
                bot,
                chat_id=chat_id,
                action="create_borrowed_expense",
                processing_text="Идет процесс добавления записи о долге и расходе...",
                fallback_error_text="Не удалось принять операцию долга. Попробуйте позже.",
                execute=lambda: CreateBorrowedExpenseOperation(SqlAlchemyUnitOfWork()).execute(
                    CreateBorrowedExpenseCommand(
                        project_key=bot.project_key,
                        operation_date=operation_date,
                        amount=Decimal(str(amount)),
                        chapter_code=chapter_code,
                        category_code=category_code,
                        subcategory_code=subcategory_code or None,
                        creditor=creditor,
                        coefficient=Decimal(str(coefficient)),
                        comment=comment,
                        mark_synced=False,
                    )
                ),
                render_success=lambda operation_id: render_borrowed_expense_success(
                    date,
                    category_name_to_use,
                    creditor,
                    coefficient,
                    breakdown,
                    amount,
                    comment,
                ),
                keyboard_factory=lambda operation_id: create_delete_operation_kb(
                    operation_id,
                    False,
                    storage="shared",
                ),
            )
            if not created:
                return

        elif wallet == "Вернуть долг":
            creditor = data["creditor"]
            created = await execute_create_flow(
                bot,
                chat_id=chat_id,
                action="create_repayment",
                processing_text="Идет процесс возврата долга...",
                fallback_error_text="Не удалось принять возврат долга. Попробуйте позже.",
                execute=lambda: CreateRepaymentOperation(SqlAlchemyUnitOfWork()).execute(
                    CreateRepaymentCommand(
                        project_key=bot.project_key,
                        operation_date=operation_date,
                        amount=Decimal(str(amount)),
                        creditor=creditor,
                        comment=comment,
                        mark_synced=False,
                    )
                ),
                render_success=lambda operation_id: render_repayment_success(
                    date,
                    creditor,
                    amount,
                    comment,
                ),
                keyboard_factory=lambda operation_id: create_delete_operation_kb(
                    operation_id,
                    False,
                    storage="shared",
                ),
            )
            if not created:
                return

        await send_next_operation_prompt(bot, chat_id)

    @comment_router.callback_query(DeleteOperation.filter(F.delete == True))
    async def confirm_delete_expense(query: CallbackQuery, callback_data: DeleteOperation):
        await toggle_delete_confirmation(
            query,
            operation_id=callback_data.operation_id,
            keyboard_factory=lambda operation_id, confirm: create_delete_operation_kb(
                operation_id,
                confirm,
                storage="shared",
            ),
            confirm=True,
        )

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == True))
    async def delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
        await execute_delete_flow(
            bot,
            query,
            operation_id=callback_data.operation_id,
            action="delete_expense",
            progress_text="Идет процесс удаления записи...",
            fallback_error_text="Не удалось удалить запись. Попробуйте позже.",
            execute=lambda: DeleteProjectOperation(SqlAlchemyUnitOfWork()).execute(
                project_key=bot.project_key,
                operation_id=callback_data.operation_id,
            ),
        )

    @comment_router.callback_query(ConfirmDeleteOperation.filter(F.confirm_delete == False))
    async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteOperation):
        await toggle_delete_confirmation(
            query,
            operation_id=callback_data.operation_id,
            keyboard_factory=lambda operation_id, confirm: create_delete_operation_kb(
                operation_id,
                confirm,
                storage="shared",
            ),
            confirm=False,
        )

    return comment_router

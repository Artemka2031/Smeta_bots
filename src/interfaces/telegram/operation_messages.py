from __future__ import annotations

from decimal import Decimal

from src.domain.services import BorrowingBreakdown


def render_expense_success(date: str, category_name: str, amount: Decimal | float, comment: str) -> str:
    return (
        f"<b>✨ Расход принят</b>\n"
        f"Дата: <code>{date}</code>\n"
        f"Категория: <code>{category_name}</code>\n"
        f"Сумма: <code>{amount}</code> ₽\n"
        f"Комментарий: <code>{comment}</code>\n"
    )


def render_borrowed_expense_success(
    date: str,
    category_name: str,
    creditor: str,
    coefficient: Decimal | float,
    breakdown: BorrowingBreakdown,
    amount: Decimal | float,
    comment: str,
) -> str:
    return (
        f"<b>✨ Долг и расход приняты</b>\n"
        f"Дата: <code>{date}</code>\n"
        f"Категория: <code>{category_name}</code>\n"
        f"Кредитор: <code>{creditor}</code>\n"
        f"Коэффициент: <code>{coefficient}</code>\n"
        f"Сумма расхода: <code>{breakdown.borrowing_amount}</code> ₽\n"
        f"Экономия: <code>{breakdown.saving_amount}</code> ₽\n"
        f"Сумма долга: <code>{amount}</code> ₽\n"
        f"Комментарий: <code>{comment}</code>\n"
    )


def render_repayment_success(date: str, creditor: str, amount: Decimal | float, comment: str) -> str:
    return (
        f"<b>✨ Возврат долга принят</b>\n"
        f"Дата: <code>{date}</code>\n"
        f"Кредитор: <code>{creditor}</code>\n"
        f"Сумма: <code>{amount}</code> ₽\n"
        f"Комментарий: <code>{comment}</code>\n"
    )


def render_coming_success(date: str, amount: Decimal | float, comment: str) -> str:
    return (
        f"<b>✨ Приход принят</b>\n"
        f"Дата: <code>{date}</code>\n"
        f"Категория: <code>Приходы</code>\n"
        f"Сумма: <code>{amount}</code> ₽\n"
        f"Комментарий: <code>{comment}</code>\n"
    )

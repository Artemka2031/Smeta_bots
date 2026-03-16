from enum import StrEnum


class OperationType(StrEnum):
    EXPENSE = "expense"
    COMING = "coming"
    BORROWED_EXPENSE = "borrowed_expense"
    REPAYMENT = "repayment"

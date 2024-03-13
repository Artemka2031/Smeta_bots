from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DeleteOperation(CallbackData, prefix="DelE"):
    operation_id: int
    delete: bool


class ConfirmDeleteOperation(CallbackData, prefix="ConfDE"):
    operation_id: int
    confirm_delete: bool


def create_delete_operation_kb(operation_id: int, confirm: bool):
    delete_b = InlineKeyboardBuilder()

    if not confirm:
        delete_b.button(text="Удалить", callback_data=DeleteOperation(operation_id=operation_id, delete=True).pack())
    else:
        delete_b.button(text="Удалить",
                        callback_data=ConfirmDeleteOperation(operation_id=operation_id, confirm_delete=True).pack())
        delete_b.button(text="Отмена",
                        callback_data=ConfirmDeleteOperation(operation_id=operation_id, confirm_delete=False).pack())

    return delete_b.as_markup()

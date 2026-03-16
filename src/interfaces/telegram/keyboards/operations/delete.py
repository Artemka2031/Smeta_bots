from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DeleteOperation(CallbackData, prefix="DelE"):
    operation_id: int
    delete: bool
    storage: str = "shared"


class ConfirmDeleteOperation(CallbackData, prefix="ConfDE"):
    operation_id: int
    confirm_delete: bool
    storage: str = "shared"


def create_delete_operation_kb(operation_id: int, confirm: bool, storage: str = "shared"):
    delete_b = InlineKeyboardBuilder()

    if not confirm:
        delete_b.button(
            text="Удалить",
            callback_data=DeleteOperation(operation_id=operation_id, delete=True, storage=storage).pack(),
        )
    else:
        delete_b.button(
            text="Удалить",
            callback_data=ConfirmDeleteOperation(
                operation_id=operation_id,
                confirm_delete=True,
                storage=storage,
            ).pack(),
        )
        delete_b.button(
            text="Отмена",
            callback_data=ConfirmDeleteOperation(
                operation_id=operation_id,
                confirm_delete=False,
                storage=storage,
            ).pack(),
        )

    return delete_b.as_markup()


class DeleteComing(CallbackData, prefix="DelC"):
    operation_id: int
    delete: bool
    storage: str = "shared"


class ConfirmDeleteComing(CallbackData, prefix="ConfDC"):
    operation_id: int
    confirm_delete: bool
    storage: str = "shared"


def create_delete_coming_kb(operation_id: int, confirm: bool, storage: str = "shared"):
    delete_b = InlineKeyboardBuilder()

    if not confirm:
        delete_b.button(
            text="Удалить",
            callback_data=DeleteComing(operation_id=operation_id, delete=True, storage=storage).pack(),
        )
    else:
        delete_b.button(
            text="Удалить",
            callback_data=ConfirmDeleteComing(
                operation_id=operation_id,
                confirm_delete=True,
                storage=storage,
            ).pack(),
        )
        delete_b.button(
            text="Отмена",
            callback_data=ConfirmDeleteComing(
                operation_id=operation_id,
                confirm_delete=False,
                storage=storage,
            ).pack(),
        )

    return delete_b.as_markup()

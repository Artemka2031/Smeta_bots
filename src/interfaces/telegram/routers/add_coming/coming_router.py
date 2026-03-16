from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.interfaces.telegram.keyboards.operations.category import create_today_kb
from src.interfaces.telegram.routers.add_coming.steps.amount_router import create_amount_router
from src.interfaces.telegram.routers.add_coming.steps.category_router import create_category_router
from src.interfaces.telegram.routers.add_coming.steps.comment_router import create_comment_router
from src.interfaces.telegram.routers.add_coming.steps.date_router import create_date_router
from src.interfaces.telegram.routers.add_coming.coming_state_class import Coming
from src.interfaces.telegram.commands import bot_commands
from src.interfaces.telegram.project_bot import ProjectBot
from src.interfaces.telegram.flow_utils import cancel_operation_flow


def create_comings_router(bot: ProjectBot):
    comings_router = Router()

    @comings_router.message(Command(bot_commands.add_coming))
    @comings_router.message(F.text.casefold() == "приход ₽")
    async def start_expense_adding(message: Message, state: FSMContext) -> None:
        await state.clear()
        sent_message = await message.answer(text="Выберете дату прихода:",
                                            reply_markup=create_today_kb())
        await state.update_data(date_message_id=sent_message.message_id)
        await state.set_state(Coming.date)

    @comings_router.message(Command("cancel_coming"))
    @comings_router.message(F.text.casefold() == "отмена прихода")
    async def delete_expense_adding(message: Message, state: FSMContext) -> None:
        await cancel_operation_flow(
            bot,
            message,
            state,
            tracked_fields=["date_message_id", "chapter_message_id", "amount_message_id", "comment_message_id"],
            cancel_text="Приход отменён",
        )

    # Добавляем роутеры по работе с датой, категориями, суммой расхода и комментариями
    comings_router.include_router(create_date_router(bot))
    comings_router.include_router(create_category_router(bot))
    comings_router.include_router(create_amount_router(bot))
    comings_router.include_router(create_comment_router(bot))

    return comings_router

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.interfaces.telegram.keyboards.operations.category import chapters_choose_kb, ChooseChapterCallback
from src.interfaces.telegram.keyboards.operations.wallet import ChooseWalletCallback, ChooseCreditorCallback, creditors_keyboard, \
    create_wallet_keyboard
from src.interfaces.telegram.routers.add_expense.expense_state_class import Expense
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.use_cases import GetProjectCatalog


def create_wallet_router(bot: ProjectBot):
    wallet_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    @wallet_router.callback_query(ChooseWalletCallback.filter(F.wallet == "Проект"))
    async def choose_project_wallet(query: CallbackQuery, state: FSMContext):
        await query.message.edit_text("Выбран кошелек: Проект", reply_markup=None)
        await state.update_data(wallet="Проект")
        chapters = await project_catalog.get_expense_chapters()

        # Создаем сообщение с выбором раздела
        chapter_message = await query.message.edit_text(
            text=f"Выбран: Проект. \nВыберите раздел:",
            reply_markup=chapters_choose_kb(chapters)
        )
        await state.update_data(chapter_message_id=chapter_message.message_id)
        await state.set_state(Expense.chapter_code)

    @wallet_router.callback_query(ChooseWalletCallback.filter(F.wallet == "Взять в долг"))
    async def choose_debt_wallet(query: CallbackQuery, state: FSMContext):
        await query.message.edit_text("Выбран кошелек: Взять в долг", reply_markup=None)
        await state.update_data(wallet="Взять в долг")
        creditors_list = await project_catalog.get_creditors()

        # Создаем клавиатуру для выбора кредиторов
        kb = creditors_keyboard(creditors_list)
        await query.message.edit_text("Выберите кредитора:", reply_markup=kb)
        await state.set_state(Expense.creditor_borrow)

    @wallet_router.callback_query(ChooseWalletCallback.filter(F.wallet == "Вернуть долг"))
    async def choose_return_debt_wallet(query: CallbackQuery, state: FSMContext):
        await query.message.edit_text("Выбран кошелек: Вернуть долг", reply_markup=None)
        await state.update_data(wallet="Вернуть долг")
        creditors_list = await project_catalog.get_creditors()

        # Создаем клавиатуру для выбора кредиторов
        kb = creditors_keyboard(creditors_list)
        await query.message.edit_text("Выберите кредитора для возврата долга:", reply_markup=kb)
        await state.set_state(Expense.creditor_return)

    @wallet_router.callback_query(ChooseCreditorCallback.filter(F.creditor == "Назад"))
    async def back_to_wallet_selection(query: CallbackQuery, state: FSMContext):
        await query.message.edit_text("Выберите кошелек:", reply_markup=create_wallet_keyboard())
        await state.set_state(Expense.wallet)  # Переход обратно к выбору кошелька

    @wallet_router.callback_query(Expense.creditor_borrow, ChooseCreditorCallback.filter())
    async def choose_creditor(query: CallbackQuery, callback_data: ChooseCreditorCallback, state: FSMContext):
        creditor = callback_data.creditor
        await query.message.edit_text(f"Выбран кредитор: {creditor}", reply_markup=None)
        await state.update_data(creditor=creditor)

        chapters = await project_catalog.get_expense_chapters()

        # Создаем сообщение с выбором раздела
        chapter_message = await query.message.edit_text(
            f"Выбран кредитор: {creditor}. \nВыберите раздел:",
            reply_markup=chapters_choose_kb(chapters)
        )
        await state.update_data(chapter_message_id=chapter_message.message_id)
        await state.set_state(Expense.chapter_code)

    @wallet_router.callback_query(Expense.creditor_return, ChooseCreditorCallback.filter())
    async def choose_creditor_for_return_debt(query: CallbackQuery, callback_data: ChooseCreditorCallback,
                                              state: FSMContext):
        creditor = callback_data.creditor
        await query.message.edit_text(f"Возврат долга: {creditor}", reply_markup=None)
        await state.update_data(creditor=creditor)

        amount_message = await query.message.answer(text="Введите сумму возврата:")
        await state.update_data(amount_message_id=amount_message.message_id)

        await state.set_state(Expense.amount)

    @wallet_router.callback_query(Expense.chapter_code, ChooseChapterCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()
        await query.message.edit_text(text="Выберите кошелёк:", reply_markup=create_wallet_keyboard())
        await state.set_state(Expense.wallet)

    return wallet_router

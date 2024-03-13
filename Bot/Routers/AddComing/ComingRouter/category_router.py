from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Database.Tables.ComingTables import ComingCategory, ComingType
from Bot.Keyboards.Operations.category import ChooseCategoryCallback, category_choose_kb
from Bot.Keyboards.Operations.types import BackToCategoriesCallback, create_type_kb, ChooseTypeCallback
from Bot.Routers.AddComing.coming_state_class import Coming

categoryRouter = Router()


@categoryRouter.callback_query(Coming.category, ChooseCategoryCallback.filter())
async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
    await query.answer()

    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_text(text=f'Выбрана категория "{category_name}". Выберите тип:',
                                  reply_markup=create_type_kb(category_id, ComingType))
    await state.set_state(Coming.type)


@categoryRouter.callback_query(Coming.type, BackToCategoriesCallback.filter(F.back == True))
async def back_to_categories(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text(text="Выберите категорию:", reply_markup=category_choose_kb(ComingCategory))
    await state.set_state(Coming.category)


@categoryRouter.callback_query(Coming.type, ChooseTypeCallback.filter())
async def set_category(query: CallbackQuery, callback_data: ChooseTypeCallback, state: FSMContext):
    await query.answer()

    category_id = callback_data.category_id
    category_name = callback_data.category_name

    type_id = callback_data.type_id
    type_name = callback_data.type_name

    await state.update_data(category={"category_id": category_id, "category_name": category_name},
                            type={"type_id": type_id, "type_name": type_name})
    await query.message.edit_text(text=f'Выбран тип "{type_name}" в категории "{category_name}"')
    amount_message = await query.message.answer(text="Введите сумму прихода:")
    await state.update_data(amount_message_id=amount_message.message_id)

    await state.set_state(Coming.amount)

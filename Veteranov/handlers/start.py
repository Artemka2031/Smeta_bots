from aiogram import Dispatcher, types
from Veteranov.keyBoards import startKB


async def process_start_command(message: types.Message):
    await message.reply("Бот запущен", reply_markup=startKB.create_start_kb())


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])

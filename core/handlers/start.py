from aiogram.types import Message


async def command_start_handler(message: Message) -> None:
    await message.answer("Hello")
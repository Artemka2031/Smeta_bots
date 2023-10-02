from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.handlers.start import command_start_handler

start_router = Router()

@start_router.message(CommandStart())


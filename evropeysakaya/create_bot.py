from  evropeysakaya import config 
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from evropeysakaya.data_base.transaction import Transaction


class FreakTelegramBot(Bot):
    def __init__(
        self,
        token,
        parse_mode,
        transaction=None,
    ):
        super().__init__(token, parse_mode)
        self.transaction: Transaction = transaction


bot: FreakTelegramBot = FreakTelegramBot(
    token=config.settings["TOKEN"],
    parse_mode=types.ParseMode.HTML,
    transaction=Transaction("evropeysakaya/data_base/google_sheets/creds.json",
                            config.settings["sheets"])
)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

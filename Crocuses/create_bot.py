from Crocuses import config
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from Crocuses.data_base.transaction import Transaction


class SheetsTelegramBot(Bot):
    def __init__(
        self,
        token,
        parse_mode,
        transaction=None,
    ):
        super().__init__(token, parse_mode)
        self.transaction: Transaction = transaction


bot: SheetsTelegramBot = SheetsTelegramBot(
    token=config.settings["TOKEN"],
    parse_mode=types.ParseMode.HTML,
    transaction=Transaction("Crocuses/data_base/google_sheets/creds.json",
                            config.settings["sheets"])
)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

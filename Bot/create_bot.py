from aiogram import Bot
from aiogram.enums import ParseMode

from GoogleSheets import GoogleSheets
from .commands import BotCommands


class ProjectBot(Bot):
    def __init__(self, token, google_sheet_path: str = None):
        super().__init__(token, parse_mode=ParseMode.HTML)
        if google_sheet_path:
            self.google_sheets = GoogleSheets(google_sheet_path)


def set_commands(commands: BotCommands):
    for params in commands:
        print(params)

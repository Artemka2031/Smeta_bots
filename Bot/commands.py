from aiogram.types import BotCommand


class BotCommands:
    start: BotCommand
    add_expense: BotCommand

    def __init__(self):
        self.start = BotCommand(command="start", description="Вызов клавиатуры бота")
        self.add_expense = BotCommand(command="add_expense", description="Добавить расход")


bot_commands = BotCommands()


def get_all_commands(commands: BotCommands = bot_commands):
    return [commands.start, commands.add_expense]

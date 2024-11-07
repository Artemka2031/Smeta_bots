from aiogram.types import BotCommand


class BotCommands:
    edit_comings: BotCommand
    add_coming: BotCommand

    edit_expenses: BotCommand
    add_expense: BotCommand

    def __init__(self):
        self.edit_comings = BotCommand(command="edit_comings", description="Редактировать приходы")
        self.add_coming = BotCommand(command="add_coming", description="Добавить приход")

        self.edit_expenses = BotCommand(command="edit_expenses", description="Редактировать расходы")
        self.add_expense = BotCommand(command="add_expense", description="Добавить расход")


bot_commands = BotCommands()


def get_all_commands(commands: BotCommands = bot_commands):
    return [commands.edit_comings, commands.add_coming, commands.edit_expenses, commands.add_expense]


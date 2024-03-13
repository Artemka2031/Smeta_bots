from .commands import BotCommands


def set_commands(commands: BotCommands):
    for params in commands:
        print(params)

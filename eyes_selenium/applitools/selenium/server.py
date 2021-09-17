from .command_executor import CommandExecutor
from .connection import USDKConnection


def connect():
    # type: () -> CommandExecutor
    commands = CommandExecutor(USDKConnection.create())
    commands.session_init()
    return commands

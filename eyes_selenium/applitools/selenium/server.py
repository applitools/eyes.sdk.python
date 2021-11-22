from .command_executor import CommandExecutor
from .connection import USDKSharedConnection


def connect():
    # type: () -> CommandExecutor
    commands = CommandExecutor(USDKSharedConnection.create())
    commands.make_sdk()
    return commands

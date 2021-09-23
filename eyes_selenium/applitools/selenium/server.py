from .command_executor import CommandExecutor
from .connection import USDKConnection
from .sdk_server import instance


def connect():
    # type: () -> CommandExecutor
    commands = CommandExecutor(USDKConnection.create(instance.port))
    commands.session_init()
    return commands

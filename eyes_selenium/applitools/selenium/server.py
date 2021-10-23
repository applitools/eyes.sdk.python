from .command_executor import CommandExecutor
from .connection import USDKSharedConnection
from .sdk_server import instance


def connect():
    # type: () -> CommandExecutor
    commands = CommandExecutor(USDKSharedConnection.create(instance.port))
    commands.make_sdk()
    return commands

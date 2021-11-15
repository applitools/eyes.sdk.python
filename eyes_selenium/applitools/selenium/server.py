from applitools import eyes_server

from .command_executor import CommandExecutor
from .connection import USDKSharedConnection


def connect():
    # type: () -> CommandExecutor
    instance = eyes_server.get_instance()
    commands = CommandExecutor(USDKSharedConnection.create(instance.port))
    commands.make_sdk()
    return commands

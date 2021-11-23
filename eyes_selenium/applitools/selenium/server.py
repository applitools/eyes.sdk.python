from os import getcwd
from typing import Text

from .command_executor import CommandExecutor
from .connection import USDKConnection


def connect(name, version):
    # type: (Text, Text) -> CommandExecutor
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk(name, version, getcwd())
    return commands

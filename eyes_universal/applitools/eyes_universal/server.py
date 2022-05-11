import sys
import typing
from logging import getLogger
from subprocess import check_output

from pkg_resources import resource_filename

if typing.TYPE_CHECKING:
    from typing import Optional

logger = getLogger(__name__)

_platform_suffixes = {
    "darwin": "macos",
    "linux": "linux",
    "linux2": "linux",  # python2 included kernel major version
    "win32": "win.exe",
}
executable_path = resource_filename(
    "applitools.eyes_universal",
    "bin/eyes-universal-" + _platform_suffixes[sys.platform],
)


class SDKServer(object):
    def __init__(
        self,
        port=None,  # type: Optional[int]
        lazy=False,  # type: bool
        idle_timeout=None,  # type: Optional[int]
        executable=executable_path,  # type: str
    ):
        self.executable = executable
        command = [executable]
        if port is not None:
            command.extend(["--port", port])
        if lazy:
            command.append("--lazy")
        if idle_timeout is not None:
            command.extend(["--idle-timeout", idle_timeout])
        command.append("--fork")
        if sys.version_info < (3,) and sys.platform != "win32":
            # python2 tends to hang if there are unclosed fds owned by child process
            # close_fds is not supported by windows python2 so not using it there
            output = check_output(command, universal_newlines=True, close_fds=True)
        else:
            output = check_output(command, universal_newlines=True)
        self.port = int(output)
        logger.info("Started Universal SDK server at %s", self.port)

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

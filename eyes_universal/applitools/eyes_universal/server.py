import sys
from logging import getLogger
from subprocess import check_output

from pkg_resources import resource_filename

logger = getLogger(__name__)

_exe_name = "eyes-universal.exe" if sys.platform == "win32" else "eyes-universal"
executable_path = resource_filename("applitools.eyes_universal", "bin/" + _exe_name)


class SDKServer(object):
    def __init__(
        self,
        port=None,  # type: int
        lazy=False,  # type: bool
        idle_timeout=None,  # type: int
        executable=executable_path,  # type: str
    ):
        self.executable = executable
        self.log_file_name = None  # backward compatibility with eyes-selenium<=5.6
        command = [executable]
        if port is not None:
            command.extend(["--port", port])
        if lazy:
            command.append("--lazy")
        if idle_timeout is not None:
            command.extend(["--idle-timeout", idle_timeout])
        command.append("--fork")
        output = check_output(command, universal_newlines=True)  # nosec
        self.port = int(output)
        logger.info("Started Universal SDK server at %s", self.port)

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

import sys
import typing
from logging import getLogger
from subprocess import STDOUT, Popen
from tempfile import NamedTemporaryFile
from time import sleep

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
        singleton=True,  # type: bool
        lazy=False,  # type: bool
        idle_timeout=None,  # type: Optional[int]
        log_file_name=None,  # type: Optional[str]
        executable=executable_path,  # type: str
    ):
        if log_file_name:
            self._log_file = open(log_file_name, "w+b")
            self.log_file_name = log_file_name
        else:
            self._log_file = NamedTemporaryFile("w+b")
            self.log_file_name = self._log_file.name
        self.executable = executable
        command = [executable]
        if port is not None:
            command.extend(["--port", port])
        if not singleton:
            command.append("--no-singleton")
        if lazy:
            command.append("--lazy")
        if idle_timeout is not None:
            command.extend(["--idle-timeout", idle_timeout])
        if sys.version_info < (3,) and sys.platform != "win32":
            # python2 tends to hang if there are unclosed fds owned by child process
            # close_fds is not supported by windows python2 so not using it there
            sdk = Popen(command, stdout=self._log_file, stderr=STDOUT, close_fds=True)
        else:
            sdk = Popen(command, stdout=self._log_file, stderr=STDOUT)
        self._sdk_process = None if singleton else sdk  # leak the singleton process
        self.port = self._read_port()
        self.is_closed = False  # explicit flag because python2 calls __del__ many times
        logger.info("Started Universal SDK server at %s", self.port)

    def _read_port(self):
        while True:
            self._log_file.seek(0)
            first_line = self._log_file.readline()
            if first_line:
                return int(first_line)
            else:
                sleep(0.5)

    def close(self):
        if not self.is_closed:
            self.is_closed = True
            if self._sdk_process:
                logger.info("Terminating Universal SDK server at %s", self.port)
                self._sdk_process.terminate()
            self._log_file.close()

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

    def __del__(self):
        self.close()

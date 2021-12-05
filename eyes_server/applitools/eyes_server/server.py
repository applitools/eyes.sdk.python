import sys
from logging import getLogger
from subprocess import STDOUT, Popen
from tempfile import NamedTemporaryFile
from time import sleep

from pkg_resources import resource_filename

logger = getLogger(__name__)

_platform_suffixes = {
    "darwin": "macos",
    "linux": "linux",
    "linux2": "linux",  # python2 included kernel major version
    "win32": "win.exe",
}
executable_path = resource_filename(
    "applitools.eyes_server", "bin/eyes-universal-" + _platform_suffixes[sys.platform]
)


class SDKServer(object):
    def __init__(self, singleton=False, log_file_name=None, executable=executable_path):
        # type: (bool, str, str) -> None
        if log_file_name:
            self._log_file = open(log_file_name, "w+b")
            self.log_file_name = log_file_name
        else:
            self._log_file = NamedTemporaryFile("w+b")
            self.log_file_name = self._log_file.name
        self.executable = executable
        command = [executable] if singleton else [executable, "--no-singleton"]
        self._sdk_process = Popen(
            command, stdout=self._log_file, stderr=STDOUT, close_fds=True
        )
        self.port = self._read_port()
        if singleton:
            self._sdk_process = None  # leak the process, it self-terminates being idle
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
            logger.info("Quit Universal SDK server at %s", self.port)
            if self._sdk_process:
                self._sdk_process.terminate()
            self._log_file.close()

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

    def __del__(self):
        self.close()

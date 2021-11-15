import sys
from logging import getLogger
from subprocess import STDOUT, Popen
from tempfile import NamedTemporaryFile
from time import sleep

from pkg_resources import resource_filename


class SDKServer(object):
    def __init__(self, executable_path, log_file_name=None):
        self.logger = getLogger(__name__)
        if log_file_name:
            self._log_file = open(log_file_name, "w+b")
            self.log_file_name = log_file_name
        else:
            self._log_file = NamedTemporaryFile("w+b")
            self.log_file_name = self._log_file.name
        self.executable_path = executable_path
        self._sdk_process = Popen(
            [executable_path, "--no-singleton"], stdout=self._log_file, stderr=STDOUT
        )
        self.port = self._read_port()
        self.logger.info("Started Universal SDK server at %s", self.port)

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
            self.logger.info("Quit Universal SDK server at %s", self.port)
            self._sdk_process.terminate()
            self._log_file.close()

    @property
    def is_closed(self):
        return self._sdk_process.returncode is not None

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

    def __del__(self):
        self.close()


_platform_suffixes = {"darwin": "macos", "linux": "linux", "win32": "win.exe"}
executable_path = resource_filename(
    "applitools.eyes_server", "bin/eyes-universal-" + _platform_suffixes[sys.platform]
)

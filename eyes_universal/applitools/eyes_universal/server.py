import atexit
import sys
import weakref
from logging import getLogger
from subprocess import Popen
from tempfile import TemporaryFile
from time import sleep

from pkg_resources import resource_filename

logger = getLogger(__name__)

_exe_name = "eyes-universal.exe" if sys.platform == "win32" else "eyes-universal"
executable_path = resource_filename("applitools.eyes_universal", "bin/" + _exe_name)
_unclosed_sdk_servers = set()


class SDKServer(object):
    log_file_name = None  # backward compatibility with eyes-selenium<=5.6

    def __init__(self):
        self.port = None
        self._usdk_subprocess = None
        self._start_usdk()

    def __del__(self):
        if self._usdk_subprocess:
            self.close()

    def __repr__(self):
        return "SDKServer(port={})".format(self.port)

    def close(self):
        self.port = None
        self._usdk_subprocess.terminate()
        self._usdk_subprocess.wait()
        self._usdk_subprocess = None
        _unclosed_sdk_servers.remove(weakref.ref(self))

    def _start_usdk(self):
        command = [executable_path, "--no-singleton"]
        with TemporaryFile("w+b") as stdout:
            self._usdk_subprocess = Popen(command, stdout=stdout)
            _unclosed_sdk_servers.add(weakref.ref(self))
            self.port = self._read_port(stdout)
        logger.info("Started Universal SDK server at %s", self.port)

    @staticmethod
    def _read_port(file):
        while True:
            file.seek(0)
            first_line = file.readline()
            if first_line:
                return int(first_line)
            else:
                sleep(0.1)


@atexit.register
def _close_unclosed_sdk_servers():
    # iterate over _unclosed_sdk_servers copy as server.close modifies it
    for server in list(_unclosed_sdk_servers):
        server = server()
        if server:
            server.close()

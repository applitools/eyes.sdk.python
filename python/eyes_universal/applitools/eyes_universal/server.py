import atexit
import sys
import weakref
from logging import getLogger
from subprocess import Popen  # nosec
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
        """Start eyes-universal service subprocess and obtain its port number."""
        self.port = None
        self._stdout_file = None
        self._usdk_subprocess = None
        self._start_usdk()

    def __del__(self):
        """Close leaked SDKServer object if it was not closed already."""
        if self._usdk_subprocess:
            self.close()

    def __repr__(self):
        """Produce helpful debugging description."""
        return "SDKServer(port={})".format(self.port)

    def close(self):
        """Terminate started universal sdk subprocess and clean up temporary file."""
        self._usdk_subprocess.terminate()
        self._usdk_subprocess.wait()
        self._usdk_subprocess = None
        self._stdout_file.close()
        self._stdout_file = None
        _unclosed_sdk_servers.remove(weakref.ref(self))
        self.port = None

    def _start_usdk(self):
        command = [executable_path, "--no-singleton"]
        self._stdout_file = TemporaryFile("w+b")
        self._usdk_subprocess = Popen(command, stdout=self._stdout_file)  # nosec
        _unclosed_sdk_servers.add(weakref.ref(self))
        self.port = self._read_port()
        logger.info("Started Universal SDK server at %s", self.port)

    def _read_port(self):
        while True:
            self._stdout_file.seek(0)
            first_line = self._stdout_file.readline()
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

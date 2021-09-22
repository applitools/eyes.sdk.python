from subprocess import STDOUT, Popen
from tempfile import NamedTemporaryFile
from time import sleep


class USDKServer(object):
    def __init__(self, executable_path, log_file_name=None):
        if log_file_name:
            self._log_file = open(log_file_name, "w+b")
            self.log_file_name = log_file_name
        else:
            self._log_file = NamedTemporaryFile("w+b")
            self.log_file_name = self._log_file.name
        self._sdk_process = Popen(
            [executable_path, "--no-singleton"], stdout=self._log_file, stderr=STDOUT
        )
        self.is_closed = False
        self.port = self._read_port()

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
            self._sdk_process.terminate()
            self._log_file.close()
            self.is_closed = True

    def __del__(self):
        self.close()

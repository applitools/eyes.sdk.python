import os
import stat
import sys
from subprocess import STDOUT, Popen
from tempfile import NamedTemporaryFile
from time import sleep

from six.moves.urllib import request

from applitools.common import logger


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
        logger.info(
            "Started Universal SDK server", log_file=self.log_file_name, port=self.port
        )

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
            logger.info(
                "Quit Universal SDK server", log_file=self.log_file_name, port=self.port
            )
            self._sdk_process.terminate()
            self._log_file.close()
            self.is_closed = True

    def __del__(self):
        self.close()


def _locked_download_binary(output_path=None):
    file_name = {
        "darwin": "cli-macos",
        "linux": "cli-linux",
        "win32": "cli-win.exe",
    }[sys.platform]
    output_path = os.path.abspath(output_path or file_name)
    downloading_path = output_path + ".downloading"
    while not os.path.exists(output_path):
        if os.path.exists(downloading_path):
            sleep(1)
        else:
            _download_binary(downloading_path, file_name)
            os.rename(downloading_path, output_path)
    return output_path


def _download_binary(output_path, file_name):
    universal_sdk_version = "0.1.4"
    binary_url = (
        "https://github.com/applitools/eyes.sdk.javascript1/releases/download/"
        "%40applitools%2Feyes-universal%40{version}/{file_name}"
    ).format(version=universal_sdk_version, file_name=file_name)
    logger.info("Downloading Universal SDK Server binary", output_path=output_path)
    try:
        request.urlretrieve(binary_url, output_path)
        os.chmod(output_path, os.stat(output_path).st_mode | stat.S_IXUSR)
    except Exception:
        os.remove(output_path)
        logger.exception("Failed to download Universal SDK Server binary")
        raise


instance = USDKServer(_locked_download_binary())

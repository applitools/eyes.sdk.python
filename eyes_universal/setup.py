from os import chmod, path
from sys import platform

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


download_url_template = (
    "https://github.com/applitools/eyes.sdk.javascript1/releases/download/"
    "%40applitools%2Feyes-universal%40{version}/{file}"
)


def current_os():
    if platform == "darwin":
        return "macos"
    elif platform == "win32":
        return "win.exe"
    if platform in ("linux", "linux2"):
        if path.exists("/etc/alpine-release"):
            return "alpine"
        else:
            return "linux"


class build_py(_build_py):  # noqa
    user_options = _build_py.user_options + [
        ("os-name=", None, "os to get binaries for (alpine,linux,macos,win.exe)")
    ]

    def initialize_options(self):
        self.os_name = current_os()  # noqa
        _build_py.initialize_options(self)

    def get_data_files(self):
        version = self.distribution.get_version()
        file_name = "eyes-universal-" + self.os_name
        target = path.join("applitools", "eyes_universal", "bin", "eyes-universal")
        if not path.isfile(target):
            url = download_url_template.format(version=version, file=file_name)
            self.mkpath(path.dirname(target))
            urlretrieve(url, target)
            chmod(target, 0o755)
        return _build_py.get_data_files(self)


setup(cmdclass={"build_py": build_py})

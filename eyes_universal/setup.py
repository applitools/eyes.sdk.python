from os import chmod, path

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


class build_py(_build_py):
    user_options = _build_py.user_options + [
        ("os-names=", None, "os to get binaries for (linux,macos,win)")
    ]

    def initialize_options(self):
        self.os_names = "linux,macos,win"
        _build_py.initialize_options(self)

    def get_data_files(self):
        version = self.distribution.get_version()
        os_binaries = {
            "linux": "eyes-universal-linux",
            "macos": "eyes-universal-macos",
            "win": "eyes-universal-win.exe",
        }
        for os in self.os_names.split(","):
            file_name = os_binaries[os]
            target = path.join("applitools", "eyes_universal", "bin", file_name)
            if not path.isfile(target):
                url = download_url_template.format(version=version, file=file_name)
                self.mkpath(path.dirname(target))
                urlretrieve(url, target)
                chmod(target, 0o755)
        return _build_py.get_data_files(self)


setup(cmdclass={"build_py": build_py})

from distutils.util import get_platform
from os import chmod, path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


download_dir = (
    "https://github.com/applitools/eyes.sdk.javascript1/releases/download/"
    "%40applitools%2Feyes-universal%40"
)


class build_py(_build_py):
    def get_data_files(self):
        platform = get_platform()
        if "linux" in platform:
            file_name = "eyes-universal-linux"
        elif "macosx" in platform:
            file_name = "eyes-universal-macos"
        elif "win" in platform:
            file_name = "eyes-universal-win.exe"
        else:
            raise RuntimeError("Unsupported platform", platform)
        target = path.join("applitools", "eyes_universal", "bin", file_name)
        url = "{}{}/{}".format(download_dir, self.distribution.get_version(), file_name)
        if not path.isfile(target):
            self.mkpath(path.dirname(target))
            urlretrieve(url, target)
            chmod(target, 0o755)
        return _build_py.get_data_files(self)


setup(cmdclass={"build_py": build_py})

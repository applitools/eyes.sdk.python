import os.path
import subprocess

import pytest

from applitools.eyes_universal import __version__ as eyes_universal_version
from applitools.selenium.__version__ import __version__ as eyes_selenium_version
from EyesLibrary.__version__ import __version__ as eyes_robotframework_version

here = os.path.dirname(__file__)
root_dir = os.path.normpath(os.path.join(here, os.pardir))


@pytest.fixture
def eyes_universal_installed(venv):
    wheels = os.path.join(root_dir, "eyes_universal", "dist")
    pip = [venv.python, "-m", "pip", "install", "--no-index", "--find-links", wheels]
    subprocess.check_call(pip + ["eyes_universal==" + eyes_universal_version])


@pytest.fixture
def eyes_selenium_installed(venv, eyes_universal_installed):
    file_name = "eyes_selenium-{}.tar.gz".format(eyes_selenium_version)
    eyes_selenium = os.path.join(root_dir, "eyes_selenium", "dist", file_name)
    pip = [venv.python, "-m", "pip", "install"]
    subprocess.check_call(pip + [eyes_selenium])


@pytest.fixture
def eyes_robotframework_installed(venv, eyes_universal_installed):
    file_name = "eyes_selenium-{}.tar.gz".format(eyes_selenium_version)
    eyes_selenium = os.path.join(root_dir, "eyes_selenium", "dist", file_name)
    file_name = "eyes-robotframework-{}.tar.gz".format(eyes_robotframework_version)
    eyes_robot = os.path.join(root_dir, "eyes_robotframework", "dist", file_name)
    pip = [venv.python, "-m", "pip", "install"]
    subprocess.check_call(pip + [eyes_selenium, eyes_robot])


def test_setup_eyes_universal(venv, eyes_universal_installed):
    get_version = [venv.python, "-m", "applitools.eyes_universal", "--version"]
    assert str(venv.get_version("eyes-universal")) == eyes_universal_version
    assert (
        eyes_universal_version.encode() == subprocess.check_output(get_version).rstrip()
    )


def test_setup_eyes_selenium(venv, eyes_selenium_installed):
    assert str(venv.get_version("eyes-selenium")) == eyes_selenium_version
    subprocess.check_call([venv.python, "-c", "from applitools.selenium import *"])


def test_setup_eyes_robot(venv, eyes_robotframework_installed):
    assert str(venv.get_version("eyes-robotframework")) == eyes_robotframework_version
    subprocess.check_call([venv.python, "-c", "from EyesLibrary import *"])

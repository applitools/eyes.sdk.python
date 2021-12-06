import os.path
import subprocess

here = os.path.dirname(os.path.join(__file__))
root_dir = os.path.normpath(os.path.join(here, os.pardir))


def _packages_resolver(
    server=False,
    selenium=False,
    robotframework=False,
):
    server_pkg, selenium_pkg, robotframework_pkg = (
        "eyes_universal",
        "eyes_selenium",
        "eyes_robotframework",
    )

    if server:
        pack = server_pkg
    elif selenium:
        pack = selenium_pkg
    elif robotframework:
        pack = robotframework_pkg
    else:
        return None
    return str(os.path.join(root_dir, pack))


def test_setup_eyes_selenium(venv):
    venv.install(_packages_resolver(server=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    assert venv.get_version("eyes-universal")
    assert venv.get_version("eyes-selenium")


def test_setup_eyes_robot(venv):
    venv.install(_packages_resolver(server=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    venv.install(_packages_resolver(robotframework=True), editable=True)
    assert venv.get_version("eyes-universal")
    assert venv.get_version("eyes-selenium")
    assert venv.get_version("eyes-robotframework")


def test_eyes_selenium_namespace_package(venv):
    venv.install(_packages_resolver(server=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from applitools.selenium import *"])


def test_eyes_robot_namespace_package(venv):
    venv.install(_packages_resolver(server=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    venv.install(_packages_resolver(robotframework=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from EyesLibrary import *"])

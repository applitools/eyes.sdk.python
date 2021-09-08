import os.path
import subprocess

here = os.path.dirname(os.path.join(__file__))
root_dir = os.path.normpath(os.path.join(here, os.pardir))


def _packages_resolver(
    common=False, core=False, selenium=False, images=False, robotframework=False
):
    common_pkg, core_pkg, selenium_pkg, images_pkg, robotframework_pkg = (
        "eyes_common",
        "eyes_core",
        "eyes_selenium",
        "eyes_images",
        "eyes_robotframework",
    )

    if common:
        pack = common_pkg
    elif core:
        pack = core_pkg
    elif selenium:
        pack = selenium_pkg
    elif images:
        pack = images_pkg
    elif robotframework:
        pack = robotframework_pkg
    else:
        return None
    return str(os.path.join(root_dir, pack))


def test_setup_eyes_common(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    assert venv.get_version("eyes-common")


def test_setup_eyes_core(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    assert venv.get_version("eyes-common")
    assert venv.get_version("eyes-core")


def test_setup_eyes_images(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(images=True), editable=True)
    assert venv.get_version("eyes-common")
    assert venv.get_version("eyes-core")
    assert venv.get_version("eyes-images")


def test_setup_eyes_selenium(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    assert venv.get_version("eyes-common")
    assert venv.get_version("eyes-core")
    assert venv.get_version("eyes-selenium")


def test_setup_eyes_robot(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    venv.install(_packages_resolver(robotframework=True), editable=True)
    assert venv.get_version("eyes-common")
    assert venv.get_version("eyes-core")
    assert venv.get_version("eyes-selenium")
    assert venv.get_version("eyes-robotframework")


def test_eyes_common_namespace_package(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from applitools.common import *"])


def test_eyes_core_namespace_package(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from applitools.core import *"])


def test_eyes_images_namespace_package(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(images=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from applitools.images import *"])


def test_eyes_selenium_namespace_package(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from applitools.selenium import *"])


def test_eyes_robot_namespace_package(venv):
    venv.install(_packages_resolver(common=True), editable=True)
    venv.install(_packages_resolver(core=True), editable=True)
    venv.install(_packages_resolver(selenium=True), editable=True)
    venv.install(_packages_resolver(robotframework=True), editable=True)
    subprocess.check_call([venv.python, "-c", "from EyesLibrary import *"])

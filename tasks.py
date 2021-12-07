import os
import sys
from os import path

from invoke import task

here = path.dirname(path.abspath(__file__))


@task
def clean(c, docs=False, bytecode=False, dist=True, extra=""):
    patterns = ["build", "*/temp"]
    if docs:
        patterns.append("docs/_build")
    if bytecode:
        patterns.append("**/*.pyc")
    if dist:
        patterns.append("**/dist")
        patterns.append("**/build")
        patterns.append("**/*.egg-info")
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task(pre=[clean])
def dist(
    c,
    universal=False,
    selenium=False,
    robotframework=False,
    prod=False,
    from_env=False,
):
    git_status = c.run("git status", hide=True)
    if "Changes not staged for commit" in git_status.stdout:
        raise Exception("Working directory should be clean")

    packages = list(
        _packages_resolver(
            universal,
            selenium,
            robotframework,
            full_path=True,
            path_as_str=True,
        )
    )
    if from_env:
        twine_command = "twine upload dist/*"
    else:
        twine_command = "twine upload --verbose -r {dest} dist/*".format(
            dest="pypi" if prod else "test"
        )
    for pack_path in packages:
        with c.cd(pack_path):
            c.run("python setup.py sdist", echo=True)
            c.run(twine_command, echo=True)


@task
def install_requirements(c, dev=False, testing=False, lint=False):
    dev_requires = [
        "bump2version",
        "pre-commit",
        "twine",
        "wheel",
    ]
    testing_requires = [
        "PyYAML",
        "mock",
        "pytest-venv==0.2.1",
        "pytest-xdist==1.26.1",
        "pytest==3.9.3",
        "requests",
        "tox==3.14.3",
        "virtualenv==20.4.0",
        "webdriver_manager==" + ("2.4.0" if sys.version_info[:1] >= (3,) else "1.5"),
    ]
    if testing:
        requires = testing_requires
    elif dev:
        requires = dev_requires
    else:
        requires = dev_requires + testing_requires
    c.run("pip install {}".format(" ".join(requires)), echo=True)


def _packages_resolver(
    universal=False,
    selenium=False,
    robotframework=False,
    full_path=False,
    path_as_str=False,
):
    packages = []
    universal_pkg, selenium_pkg, robot_pkg = (
        "eyes_universal",
        "eyes_selenium",
        "eyes_robotframework",
    )
    if universal:
        packages.append(universal_pkg)
    if selenium:
        packages.append(selenium_pkg)
    if robotframework:
        packages.append(robot_pkg)
    if not packages:
        packages = [universal_pkg, selenium_pkg, robot_pkg]

    for pack in packages:
        if full_path:
            pack = path.join(here, pack)
            if path_as_str:
                pack = str(pack)
        yield pack


@task
def install_packages(
    c,
    universal=False,
    selenium=False,
    robotframework=False,
    editable=False,
):
    packages = _packages_resolver(
        universal,
        selenium,
        robotframework,
        full_path=True,
        path_as_str=True,
    )

    editable = "-e" if editable else ""
    if sys.platform == "darwin":
        # This is needed to find zlib when installing pillow on osx+xcode
        xcode_sdk_path = c.run("xcrun --show-sdk-path", hide=True).stdout.strip()
        env = {"CPATH": xcode_sdk_path + "/usr/include"}
    else:
        env = {}
    for pack in packages:
        c.run("pip install -U {} {}".format(editable, pack), echo=True, env=env)


@task
def pep_check(c, selenium=False):
    for pack in _packages_resolver(selenium=selenium, full_path=True):
        c.run("flake8 {}".format(pack), echo=True)


@task
def mypy_check(c, selenium=False):
    for pack in _packages_resolver(selenium=selenium, full_path=True):
        c.run(
            "mypy --no-incremental --ignore-missing-imports {}/applitools".format(pack),
            echo=True,
        )


@task
def run_tests_on_CI(c, tests):
    browsers = os.getenv("TEST_BROWSERS", "").split(",")
    if not browsers:
        raise ValueError("`TEST_BROWSERS` env variable should be set")

    pattern = (
        "pytest {par} {tests} "
        "--ignore={tests}/test_dom_capture.py "
        "--ignore={tests}/test_client_sites.py".format(
            par="-n6" if bool(os.getenv("TEST_REMOTE", False)) else "-n2",
            tests=tests,
        )
    )

    c.run(pattern, echo=True)


@task
def gen_robot_docs(c):
    c.run(
        "python -m robot.libdoc --format html EyesLibrary   docs/eyes_robotframework/keywords.html"
    )

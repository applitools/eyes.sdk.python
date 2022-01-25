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
        patterns.append("dist")
        patterns.append("**/dist")
        patterns.append("**/build")
        patterns.append("**/*.egg-info")
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task(pre=[clean])
def build_packages(c, universal=False, selenium=False, robotframework=False):
    packages = list(_packages_resolver(universal, selenium, robotframework))
    dist = path.abspath("dist")
    for package_dir in packages:
        if package_dir == "eyes_universal":
            build_cmd = "./build_wheels.sh --dist-dir=" + dist
        else:
            build_cmd = "python setup.py sdist --dist-dir=" + dist
        with c.cd(package_dir):
            c.run(build_cmd, echo=True)


@task(pre=[clean])
def dist(
    c,
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
            selenium=selenium,
            robotframework=robotframework,
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
        '"pytest-xdist<2"',
        '"pytest<5"',
        "requests",
        "tox==3.24.5",
        "virtualenv==20.11",
        "webdriver_manager==" + ("3.5.2" if sys.version_info[:1] >= (3,) else "1.5"),
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
def gen_robot_docs(c):
    c.run(
        "python -m robot.libdoc --format html EyesLibrary   docs/eyes_robotframework/keywords.html"
    )

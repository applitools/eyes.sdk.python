import os
import shutil
from os import path

from invoke import task

here = path.dirname(path.abspath(__file__))


@task
def clean(c, docs=False, bytecode=False, dist=True, node=True, extra=""):
    patterns = ["build", "*/temp"]
    if docs:
        patterns.append("docs/_build")
    if bytecode:
        patterns.append("**/*.pyc")
    if dist:
        patterns.append("**/dist")
        patterns.append("**/build")
        patterns.append("**/*.egg-info")
    if node:
        patterns.append("*/node_modules")
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task(pre=[clean])
def dist(
    c,
    common=False,
    core=False,
    selenium=False,
    images=False,
    prod=False,
    from_env=False,
):
    git_status = c.run("git status", hide=True)
    if "Changes not staged for commit" in git_status.stdout:
        raise Exception("Working directory should be clean")

    packages = list(
        _packages_resolver(
            common, core, selenium, images, full_path=True, path_as_str=True
        )
    )
    _fetch_js_libs_if_required(c, common, core, images, selenium)

    if from_env:
        twine_command = "twine upload dist/*"
    else:
        twine_command = "twine upload -r {dest} dist/*".format(
            dest="pypi" if prod else "test"
        )
    for pack_path in packages:
        with c.cd(pack_path):
            c.run("python setup.py sdist", echo=True)
            c.run(twine_command, echo=True)


@task
def install_requirements(c, dev=False, testing=False, lint=False):
    dev_requires = [
        "ipython",
        "ipdb",
        "bump2version",
        "wheel",
        "twine",
        "pre-commit",
        "browser_cookie3",
    ]
    testing_requires = [
        "pytest==3.9.3",
        "pytest-cov==2.6.1",
        "pytest-xdist==1.26.1",
        "PyYAML",
        "virtualenv==16.3.0",
        "pytest-virtualenv==1.4.0",
        "mock",
        "webdriver_manager==1.5",
        "tox==3.14.3",
    ]
    lint_requires = [
        "flake8",
        "flake8-import-order",
        "flake8-bugbear",
        "mypy",
    ]
    if testing:
        requires = testing_requires
    elif dev:
        requires = dev_requires
    elif lint:
        requires = lint_requires
    else:
        requires = dev_requires + testing_requires + lint_requires
    c.run("pip install {}".format(" ".join(requires)), echo=True)


def _packages_resolver(
    common=False,
    core=False,
    selenium=False,
    images=False,
    full_path=False,
    path_as_str=False,
):
    packages = []
    common_pkg, core_pkg, selenium_pkg, images_pkg = (
        "eyes_common",
        "eyes_core",
        "eyes_selenium",
        "eyes_images",
    )
    if common:
        packages.append(common_pkg)
    if core:
        packages.append(core_pkg)
    if selenium:
        packages.append(selenium_pkg)
    if images:
        packages.append(images_pkg)

    if not packages:
        packages = [common_pkg, core_pkg, selenium_pkg, images_pkg]

    for pack in packages:
        if full_path:
            pack = path.join(here, pack)
            if path_as_str:
                pack = str(pack)
        yield pack


def _fetch_js_libs_if_required(c, common, core, selenium, images):
    # get js libs only if selenium lib is installing
    if selenium or not any([common, core, images, selenium]):
        retrieve_js(c)


@task
def install_packages(
    c, common=False, core=False, selenium=False, images=False, editable=False
):
    packages = _packages_resolver(
        common, core, selenium, images, full_path=True, path_as_str=True
    )

    _fetch_js_libs_if_required(c, common, core, images, selenium)

    editable = "-e" if editable else ""
    for pack in packages:
        c.run("pip install -U {} {}".format(editable, pack), echo=True)


@task
def uninstall_packages(c, common=False, core=False, selenium=False, images=False):
    packages = _packages_resolver(common, core, selenium, images)
    c.run("pip uninstall {}".format(" ".join(packages)), echo=True)


@task
def pep_check(c, common=False, core=False, selenium=False, images=False):
    for pack in _packages_resolver(common, core, selenium, images, full_path=True):
        c.run("flake8 {}".format(pack), echo=True)


@task
def mypy_check(c, common=False, core=False, selenium=False, images=False):
    for pack in _packages_resolver(common, core, selenium, images, full_path=True):
        c.run(
            "mypy --no-incremental --ignore-missing-imports {}/applitools".format(pack),
            echo=True,
        )


@task
def retrieve_js(c):
    for pack in _packages_resolver(selenium=True, full_path=True):
        if path.exists(path.join(pack, "package-lock.json")):
            os.remove(path.join(pack, "package-lock.json"))

        with c.cd(pack):
            c.run("npm update --save", echo=True)
        print("Moving js for {}".format(pack))
        move_js_resources_to(pack)


def move_js_resources_to(pack):
    paths = [
        "dom-capture/dist/captureDomAndPoll.js",
        "dom-capture/dist/captureDomAndPollForIE.js",
        "dom-snapshot/dist/processPageAndSerializePoll.js",
        "dom-snapshot/dist/processPageAndSerializePollForIE.js",
    ]
    node_resources = path.join(pack, "applitools/selenium/resources/")
    node_modules = path.join(pack, "node_modules/@applitools")
    for pth in paths:
        from_ = path.join(node_modules, pth)
        name = path.basename(from_)
        to = path.join(node_resources, name)
        print("Moving js lib from {} to {}".format(from_, to))
        shutil.copy(from_, dst=to)


@task
def run_tests_on_CI(c, tests):
    browsers = os.getenv("TEST_BROWSERS", "").split(",")
    if not browsers:
        raise ValueError("`TEST_BROWSERS` env variable should be set")

    pattern = "pytest {par} {tests} --ignore={tests}/test_dom_capture.py --ignore={tests}/test_client_sites.py".format(
        par="-n6" if bool(os.getenv("TEST_REMOTE", False)) else "-n2", tests=tests
    )

    # use Unix background task execution for run tests in parallel
    command = pattern
    if browsers:
        command = "&".join(
            ["TEST_BROWSERS={} ".format(browser) + pattern for browser in browsers]
        )
    c.run(command, echo=True)

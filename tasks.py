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
def dist(c, common=False, core=False, selenium=False, images=False, prod=False):
    packages = list(
        _packages_resolver(
            common, core, selenium, images, full_path=True, path_as_str=True
        )
    )
    dest = "pypi" if prod else "test"
    for pack_path in packages:
        with c.cd(pack_path):
            c.run("python setup.py sdist", echo=True)
            c.run("twine upload -r {dest} dist/*".format(dest=dest), echo=True)


@task
def install_requirements(c, dev=False, testing=False, lint=False):
    dev_requires = ["ipython", "ipdb", "bumpversion", "wheel", "twine", "pre-commit"]
    testing_requires = [
        "pytest==3.9.3",
        "pytest-cov==2.6.1",
        "pytest-xdist==1.26.1",
        "virtualenv==16.3.0",
        "pytest-virtualenv==1.4.0",
        "mock",
        "webdriver_manager",
    ]
    lint_requires = ["flake8", "flake8-import-order", "flake8-bugbear", "mypy"]
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


@task
def install_packages(
    c, common=False, core=False, selenium=False, images=False, editable=False
):
    packages = _packages_resolver(
        common, core, selenium, images, full_path=True, path_as_str=True
    )
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
        with c.cd(pack):
            c.run("npm update", echo=True)
        move_js_resources_to(pack)


def move_js_resources_to(pack):
    paths = [
        "dom-capture/dist/captureDom.js",
        "dom-snapshot/dist/processPage.js",
        "dom-snapshot/dist/processPageAndPoll.js",
        "dom-snapshot/dist/processPageAndSerialize.js",
    ]
    node_resources = path.join(pack, "applitools/selenium/resources/")
    node_modules = path.join(pack, "node_modules/@applitools")
    for pth in paths:
        from_ = path.join(node_modules, pth)
        name = path.basename(from_)
        shutil.copy(from_, dst=path.join(node_resources, name))


@task
def run_selenium_tests(c, remote=False, headless=False, platform=None):
    sel_tests = "tests/functional/eyes_selenium/selenium"
    pattern = (
        "pytest {proc_num} --headless {headless} {"
        "remote} "
        "--platform '{platform}' "
        "--browser '%(browser)s' {tests} "
        "--ignore={tests}/test_client_sites.py"
    ).format(
        proc_num="-n 4" if remote else "",
        headless=headless,
        remote="--remote 1" if remote else "",
        platform=platform,
        tests=sel_tests,
    )
    browsers = ["firefox", "chrome"]
    if platform.lower().startswith("mac"):
        browsers.append("safari")
    elif platform.lower().startswith("windows"):
        browsers.append("internet explorer")
        browsers.append("MicrosoftEdge")

    # use Unix background task execution for run tests in parallel
    command = "&".join([pattern % dict(browser=browser) for browser in browsers])
    c.run(command, echo=True)

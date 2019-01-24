from os import path

from invoke import task

here = path.dirname(path.abspath(__file__))


@task
def clean(c, docs=False, bytecode=False, dist=True, extra=''):
    patterns = ['build']
    if docs:
        patterns.append('docs/_build')
    if bytecode:
        patterns.append('**/*.pyc')
    if dist:
        patterns.append('**/dist')
        patterns.append('**/build')
        patterns.append('**/*.egg-info')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task(pre=[clean])
def dist(c, core=None,
         selenium=None, images=None, prod=False):
    packages = list(_packages_resolver(core, selenium, images,
                                       full_path=True, path_as_str=True))
    dest = 'pypi' if prod else 'test'
    for pack_path in packages:
        with c.cd(pack_path):
            c.run("python setup.py build bdist_wheel", echo=True)
            c.run('twine upload -r {dest} dist/*'.format(dest=dest), echo=True)


@task
def install_requirements(c, dev=None, testing=None, lint=None):
    dev_requires = [
        'ipython',
        'ipdb',
        'bumpversion',
        'wheel',
        'twine',
    ]
    testing_requires = [
        'pytest==3.8.2',
        'pytest-cov',
        'pytest-xdist',
        'virtualenv',
        'pytest-virtualenv',
        'mock'
    ]
    lint_requires = [
        'flake8',
        'flake8-import-order',
        'flake8-bugbear',
        'mypy',
    ]
    if testing:
        requires = testing_requires
    elif dev:
        requires = dev_requires
    elif lint:
        requires = lint_requires
    else:
        requires = dev_requires + testing_requires + lint_requires
    c.run("pip install {}".format(' '.join(requires)), echo=True)


def _packages_resolver(core=None, selenium=None, images=None,
                       full_path=False, path_as_str=False):
    packages = []
    core_pkg, selenium_pkg, images_pkg = 'eyes_core', 'eyes_selenium', 'eyes_images'

    if core:
        packages.append(core_pkg)
    if selenium:
        packages.append(selenium_pkg)
    if images:
        packages.append(images_pkg)
    if not packages:
        packages = [core_pkg, selenium_pkg, images_pkg]

    for pack in packages:
        if full_path:
            pack = path.join(here, pack)
            if path_as_str:
                pack = str(pack)
        yield pack


@task
def install_packages(c, core=None,
                     selenium=None, images=None):
    packages = _packages_resolver(core, selenium, images,
                                  full_path=True, path_as_str=True)
    for pack in packages:
        c.run("pip install -U -e {}".format(pack), echo=True)


@task
def uninstall_packages(c, core=None,
                       selenium=None, images=None):
    packages = _packages_resolver(core, selenium, images)
    c.run("pip uninstall {}".format(' '.join(packages)), echo=True)


@task
def pep_check(c, core=None,
              selenium=None, images=None):
    for pack in _packages_resolver(core, selenium, images, full_path=True):
        c.run('flake8 {}'.format(pack), echo=True)


@task
def mypy_check(c, core=None,
               selenium=None, images=None):
    for pack in _packages_resolver(core, selenium, images, full_path=True):
        c.run('mypy --no-incremental --ignore-missing-imports {}/applitools'.format(pack), echo=True)


@task
def test_run_packs(c, core=None,
                   selenium=None, images=None):
    for pack in _packages_resolver(core, selenium, images):
        c.run('pytest tests/functional/{}'.format(pack), echo=True)


@task
def test_run_integration(c):
    c.run('pytest tests/test_integration.py')

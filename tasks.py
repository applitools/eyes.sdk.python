from pathlib import Path

from invoke import task

here = Path('.').absolute()


@task
def clean(c, docs=False, bytecode=False, extra=''):
    patterns = ['build']
    if docs:
        patterns.append('docs/_build')
    if bytecode:
        patterns.append('**/*.pyc')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task
def build(c, docs=False):
    c.run("python setup.py build")
    if docs:
        c.run("sphinx-build docs docs/_build")


@task
def install_requirements(c):
    dev_requires = [
        'ipython',
        'ipdb',
        'bumpversion',
        'flake8',
        'flake8-import-order',
        'flake8-bugbear',
        'mypy']

    testing_requires = [
        'pytest>=3.0.0',
        'pytest-cov',
        'pytest-xdist',
    ]
    requires = dev_requires + testing_requires
    c.run("pip install {}".format(' '.join(requires)))

@task
def install_packages(c):
    # d = str(here / 'eyes_core')
    d = str(here / 'eyes_selenium')
    c.run("pip install -U {}".format(d))

import codecs
import re
import sys

from pathlib import Path

from setuptools import setup, find_namespace_packages

if sys.version_info < (3, 4):
    raise RuntimeError("The Python 3.4+ is required")

here = Path('.').absolute()

def read(filename: str):
    return codecs.open(str(here / filename), 'r', 'utf-8').read()


INSTALL_REQUIRES = [
    # 'appltiools_core>=0.1.0',
    'selenium>=3.14.0',
    'tinycss2>=0.6.1'
]

if sys.version_info < (3, 5):
    # typing module was added as builtin in Python 3.5
    INSTALL_REQUIRES.append('typing >= 3.5.2')

# preventing ModuleNotFoundError caused by importing lib before installing deps
with open(str(here/'applitools/selenium/__version__.py'), 'r') as f:
    try:
        VERSION = re.findall(r"^__version__ = '([^']+)'\r?$",
                             f.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


setup(
    name='applitools_selenium',
    version=VERSION,
    packages=find_namespace_packages(include=['applitools.*']),
    url='http://www.applitools.com',
    license='Apache License, Version 2.0',
    author='Applitools Team',
    author_email='team@applitools.com',
    description='Applitools Python SDK',
    long_description=read('README.rst'),
    long_description_content_type='text/rst',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing"
    ],
    keywords='applitools eyes selenium',
    install_requires=INSTALL_REQUIRES,
    package_data={
        '': ['README.rst', 'LICENSE'],
        'core': ['py.typed'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/applitools/eyes.sdk.python/issues',
        'Source': 'https://github.com/applitools/eyes.sdk.python/tree/master/eyes_selenium/applitools/core',
    },
)

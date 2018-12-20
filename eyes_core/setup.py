import os
import re
import codecs
from os import path

from setuptools import setup
try:
    from setuptools import find_namespace_packages
except ImportError:
    raise ImportError("Please update your version of setuptools: pip install -U setuptools")

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), 'r', 'utf-8').read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version():
    with open(os.path.join(os.path.abspath('.'), 'applitools/eyes_core/__version__.py'), 'r') as f:
        try:
            version = re.findall(r"^__version__ = '([^']+)'\r?$",
                                 f.read(), re.M)[0]
        except IndexError:
            raise RuntimeError('Unable to determine version.')
    return version


setup(
    name='eyes_core',
    version=get_version(),
    packages=find_namespace_packages(include=['applitools.*'], exclude=('tests',)),
    url='http://www.applitools.com',
    license='Apache License, Version 2.0',
    author='Applitools Team',
    author_email='team@applitools.com',
    description='Applitools Python SDK. Core package',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing"
    ],
    keywords='applitools eyes eyes_core',
    install_requires=[
        'attrs>=18',
        'Pillow>=5.0.0',
        'requests>=2.1.0',
        'typing>=3.5.2; python_version<="3.4"',
    ],
    package_data={
        '':          ['README.rst', 'LICENSE'],
        'eyes_core': ['py.typed'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/applitools/eyes.sdk.python/issues',
        'Source':      'https://github.com/applitools/eyes.sdk.python/tree/master/eyes_core/applitools/eyes_core',
    },
)

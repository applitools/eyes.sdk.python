import re
import codecs
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), 'r', 'utf-8').read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version(package_name):
    version_file = read('applitools/{}/__version__.py'.format(package_name))
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             version_file, re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

    return version


setup(
    name='eyes_images',
    version=get_version('images'),
    packages=find_packages(include=['applitools.*'], exclude=('tests',)),
    url='http://www.applitools.com',
    license='Apache License, Version 2.0',
    author='Applitools Team',
    author_email='team@applitools.com',
    description='Applitools Python SDK. Images package',
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
    keywords='applitools eyes eyes_images',
    install_requires=[
        'eyes-core=={}'.format(get_version('images')),
        'Pillow>=5.0.0',
        'typing>=3.5.2; python_version<="3.4"',
    ],
    package_data={
        '':     ['README.rst', 'LICENSE'],
        'core': ['py.typed'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/applitools/eyes.sdk.python/issues',
        'Source':      'https://github.com/applitools/eyes.sdk.python/tree/master/eyes_images/applitools/images',
    },
)

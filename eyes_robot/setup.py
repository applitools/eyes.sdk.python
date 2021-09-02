# #!/usr/bin/env python
import codecs
import re
import sys
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version():
    version_file = read("src/EyesLibrary/__version__.py")
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


install_requires = [
    "trafaret == 2.1.0",
    "PyYAML >= 5",
    "eyes_selenium >= 4.21.0",
    "robotframework >= 3.2.2",
    "robotframework-pythonlibcore >= 2.2.1",
    "robotframework-seleniumlibrary >= 5.1.3",
    "robotframework-appiumlibrary >= 1.6",
]
setup(
    name="eyes-robotframework",
    version=get_version(),
    url="http://www.applitools.com",
    author="Applitools Team",
    author_email="team@applitools.com",
    description="Applitools Python SDK. Robot Framework package",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    python_requires=">=2.7, <4",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Framework :: Robot Framework :: Library",
    ],
    keywords="applitools eyes eyes_selenium selenium appium",
    install_requires=install_requires,
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={
        "": ["README.rst", "LICENSE"],
        "EyesLibrary": ["py.typed", "applitools.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/applitools/eyes.sdk.python/issues",
        "Source": "https://github.com/applitools/eyes.sdk.python/tree/master"
        "/eyes_robot",
    },
)

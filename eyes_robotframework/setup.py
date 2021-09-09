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
    "PyYAML >= 5,<6",
    "eyes_selenium >= 4.21.0",
]
if sys.version_info[:2] <= (2, 7):
    install_requires.extend(
        [
            "robotframework >= 3.2.2,<4.0 ",
            "robotframework-pythonlibcore >= 2.0.2,<3.0",
            "robotframework-seleniumlibrary >= 3.3.1,<4.5",
            "robotframework-appiumlibrary >= 1.5,<1.6",
        ]
    )
else:
    install_requires.extend(
        [
            "robotframework >= 4.0 ",
            "robotframework-pythonlibcore >= 3.0",
            "robotframework-seleniumlibrary >= 4.5",
            "robotframework-appiumlibrary >= 1.6",
        ]
    )

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
        "Development Status :: 4 - Beta",
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
    keywords="applitools robotframework eyes eyes_selenium selenium appium",
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
        "/eyes_robotframework",
    },
)

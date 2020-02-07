import codecs
import re
import sys
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version(package_name):
    version_file = read("applitools/{}/__version__.py".format(package_name))
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


install_requires = [
    "eyes-common=={}".format(get_version("selenium")),
    "eyes-core=={}".format(get_version("selenium")),
    "tinycss2==0.6.1",  # last version that supports python 2
    "selenium>=2.53.0,<4",
    "Pillow>=5.0,<7.0",  # 7 and above doesnt support python 2
    # uses for check if the mobile platform is used in the test
    "Appium-Python-Client>=0.4",
    "ua_parser==0.8",
    "attrs>=19,<20",
    "transitions>=0.6,<0.7",
    "lxml>=4.4,<5",
]
# using this way of defining instead of 'typing>=3.5.2; python_version<="3.4"'
# for run on old version of setuptools without issues
if sys.version_info < (3, 5):
    # typing module was added as builtin in Python 3.5
    install_requires.append("typing >= 3.5.2")

if sys.version_info < (3,):
    install_requires.append("futures==3.2.0")

setup(
    name="eyes_selenium",
    version=get_version("selenium"),
    packages=find_packages(),
    url="http://www.applitools.com",
    author="Applitools Team",
    author_email="team@applitools.com",
    description="Applitools Python SDK. Selenium package",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="applitools eyes eyes_selenium",
    install_requires=install_requires,
    package_data={
        "": ["README.rst", "LICENSE"],
        "applitools.selenium": ["py.typed", "resources/*.js"],
    },
    project_urls={
        "Bug Reports": "https://github.com/applitools/eyes.sdk.python/issues",
        "Source": "https://github.com/applitools/eyes.sdk.python/tree/master"
        "/eyes_selenium",
    },
)

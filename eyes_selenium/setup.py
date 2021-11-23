import codecs
import re
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


def get_version(package_name):
    version_file = read("applitools/{}/__version__.py".format(package_name))
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


setup(
    version=get_version("selenium"),
    package_data={"applitools.selenium": ["py.typed", "resources/*.js"]},
)

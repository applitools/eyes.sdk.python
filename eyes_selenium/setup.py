import sys

from setuptools import setup

install_requires = [
    "eyes-server==0.2.0",
    "selenium>=2.53.0,<4",
    # uses for check if the mobile platform is used in the test
    "ua_parser==0.10.0",
    "attrs>=19.2.0,<23",
    "transitions>=0.6,<=0.8.3",
    "lxml>=4.4,<5",
    "structlog<=20.1.0",
    "websocket-client<=0.59",
    "urllib3>=1.25.10",
    "requests>=2.22.0",
]


if sys.version_info[:2] <= (2, 7):
    install_requires.append("Pillow >= 5.0.0,<7.0.0")
    install_requires.append("Appium-Python-Client>=0.4,<1.0.0")
    install_requires.append("tinycss2==0.6.1")
else:
    install_requires.append("Pillow >= 5.0.0")
    install_requires.append("Appium-Python-Client>=0.4,<2")
    install_requires.append("tinycss2>=0.6.1,<1.1.0")

if sys.version_info[:2] <= (2, 7):
    install_requires.append("cattrs<=1.0.0")
if sys.version_info[:2] <= (3, 6):
    install_requires.append("cattrs<1.1.0")
else:
    install_requires.append("cattrs>=1.1.0")


if sys.version_info[:2] < (3, 4):
    install_requires.append("enum34==1.1.6")
# using this way of defining instead of 'typing>=3.5.2; python_version<="3.4"'
# for run on old version of setuptools without issues
if sys.version_info[:2] < (3, 5):
    # typing module was added as builtin in Python 3.5
    install_requires.append("typing >= 3.5.2")

if sys.version_info[:1] < (3,):
    install_requires.append("futures==3.2.0")

# brotli doesn't have binary distribution on py27/win64
# so let's use brotlipy there to avoid requirement to have msvc to build
if sys.version_info[:1] < (3,) and sys.platform.startswith("win"):
    install_requires.append("brotlipy==0.7.0")
else:
    install_requires.append("brotli>=1.0.9")

setup(
    install_requires=install_requires,
    package_data={
        "applitools.selenium": ["py.typed", "resources/*.js"],
    },
)

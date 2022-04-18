|Build Status| |Black Formatter|

Eyes.Sdk.Python
===============

Applitools Eyes SDK For Python (Unified Repo)


Usage
-----

Please check the applitools website for usage instructions:

-  Selenium Python example:
   https://applitools.com/tutorials/selenium-python.html

-  Python Appium native example:
   https://applitools.com/tutorials/appium-native-python.html

-  Python Appium web example:
   https://applitools.com/tutorials/appium-web-python.html

-  Python Image SDK example:
   https://applitools.com/tutorials/screenshots-python.html

-  Python Robot Framework SDK example:
   https://github.com/applitools/robotframework-quickstart

.. |Black Formatter| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
.. |Build Status| image:: https://travis-ci.com/applitools/eyes.sdk.python.svg?branch=v5.5.0
   :target: https://travis-ci.com/applitools/eyes.sdk.python


Development
-----------

For smother development experience install Invoke for task run first

::

    pip install invoke
    inv install-requirements  # install libs required for development
    inv install-packages  # for installing all packages
    inv install-packages  --core # install only core package, could be core|selenium]images
    inv dist --core  # publish eyes_core to test.pypi.org
    inv dist --core  -prod # publish eyes_core to pypi.org

Install pre-commit hook
***********************
Install `pre-commit <https://pre-commit.com/#installation>`_ for check and format code before commit. For
manage hooks you could use invoke:

::

    # installing of git hooks
    pre-commit install
    # removing of git hooks
    pre-commit uninstall


Testing
-------

For local testing, for example, images sdk

::

    inv install-packages --core --images
    tox -e images


Docs
----

Generate Robot Framework docs

::

    inv gen-robot-docs

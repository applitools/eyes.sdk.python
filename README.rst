|Build Status|

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

.. |Build Status| image:: https://travis-ci.org/applitools/eyes.sdk.python.svg?branch=master
   :target: https://travis-ci.org/applitools/eyes.sdk.python


Development
-----------

For smother development experience install Invoke for task run first

:: 

    pip install invoke
    inv install-requirements  # install libs required for development
    inv install-packages  # for installing all packages
    inv install-packages  -core # install only core package, could be core|selenium]images
    inv dist -core  # publish eyes_core to test.pypi.org
    inv dist -core  -prod # publish eyes_core to pypi.org

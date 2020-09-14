from __future__ import print_function
import time

from selenium.common.exceptions import WebDriverException


def open_webdriver(driver_callable):
    browser = None

    for i in range(5):
        try:
            browser = driver_callable()
            break
        except Exception as e:
            print(
                "Failed to start browser. Retrying {}\n "
                "Raised an exception {}".format(i, e)
            )
            time.sleep(1.0)

    if browser is None:
        raise WebDriverException("Webdriver wasn't created!")
    return browser

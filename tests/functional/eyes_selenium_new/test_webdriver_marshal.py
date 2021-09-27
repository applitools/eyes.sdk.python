from applitools.common import MatchLevel
from applitools.selenium import Target
from applitools.selenium.universal_sdk_types import (
    marshal_check_settings,
    marshal_webdriver_ref,
)


def test_marshal_webdriver_ref(local_chrome_driver):
    marshaled = marshal_webdriver_ref(local_chrome_driver)

    assert len(marshaled["sessionId"]) == 32
    assert marshaled["serverUrl"].startswith("http://127.0.0.1:")
    assert marshaled["capabilities"]["browserName"] == "chrome"


def test_check_settings():
    marshalled = marshal_check_settings(Target.region("abc"))

    assert marshalled

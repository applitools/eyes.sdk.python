import json

import pytest
import requests
from pytest_dictsdiff import check_objects

from applitools.common import RectangleSize
from applitools.common.utils import urlencode, urlsplit, urlunsplit
from applitools.selenium import Configuration, Target
from tests.utils import get_session_results


@pytest.fixture
def dom_intercepting_eyes(eyes):
    intercepted = eyes._selenium_eyes._try_capture_dom

    def try_capture_dom():
        eyes.captured_dom_json = intercepted()
        return eyes.captured_dom_json

    eyes._selenium_eyes._try_capture_dom = try_capture_dom
    return eyes


@pytest.mark.platform("Linux")
@pytest.mark.parametrize(
    "url, num",
    [
        ["https://applitools.github.io/demo/TestPages/DomTest/dom_capture.html", "1"],
        ["https://applitools.github.io/demo/TestPages/DomTest/dom_capture_2.html", "2"],
    ],
)
def test_send_DOM_1_2(eyes, driver, batch_info, url, num):
    driver.get(url)
    config = Configuration().set_batch(batch_info)
    eyes.set_configuration(config)
    eyes.open(driver, "Test Send DOM", "TestSendDOM_" + num)
    eyes.check_window()
    results = eyes.close(False)
    assert get_has_DOM(eyes.api_key, results)


def test_not_send_DOM(eyes, driver, batch_info):
    driver.get("https://applitools.com/helloworld")
    config = Configuration().set_batch(batch_info).set_send_dom(False)
    eyes.set_configuration(config)
    eyes.open(
        driver,
        "Test NOT SendDom",
        "Test NOT SendDom",
        viewport_size={"width": 1000, "height": 700},
    )
    eyes.check("window", Target.window().send_dom(False))
    results = eyes.close(False)
    assert not get_has_DOM(eyes.api_key, results)


def test_send_DOM_Selector(eyes, driver, batch_info):
    driver.get("https://applitools.github.io/demo/TestPages/DomTest/dom_capture.html")
    config = Configuration().set_batch(batch_info)
    eyes.set_configuration(config)
    eyes.open(
        driver,
        "Test SendDom",
        "Test SendDom",
        viewport_size={"width": 1000, "height": 700},
    )
    eyes.check("region", Target.region("#scroll1"))
    results = eyes.close(False)
    assert get_has_DOM(eyes.api_key, results)


@pytest.mark.expected_json("expected_dom1")
def test_send_DOM_full_window(dom_intercepting_eyes, driver, batch_info, expected_json):
    config = (
        Configuration()
        .set_batch(batch_info)
        .set_app_name("Test Send DOM")
        .set_test_name("Full Window")
        .set_viewport_size(RectangleSize(1024, 768))
        # TODO: Remove this when default options get in sync for java and python SDK
        .set_hide_scrollbars(True)
    )
    dom_intercepting_eyes.set_configuration(config)

    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    dom_intercepting_eyes.open(driver, "Test Send DOM", "Full Window")
    dom_intercepting_eyes.check("Window", Target.window().fully())
    results = dom_intercepting_eyes.close(False)
    actual = json.loads(dom_intercepting_eyes.captured_dom_json)

    assert get_has_DOM(dom_intercepting_eyes.api_key, results)
    assert check_objects(actual, expected_json)
    assert get_step_DOM(dom_intercepting_eyes, results) == expected_json


def get_has_DOM(api_key, results):
    session_results = get_session_results(api_key, results)
    actualAppOutputs = session_results["actualAppOutput"]
    assert len(actualAppOutputs) == 1
    return actualAppOutputs[0]["image"]["hasDom"]


def get_step_DOM(eyes, results):
    session_results = get_session_results(eyes.api_key, results)
    actualAppOutputs = session_results["actualAppOutput"]
    dom_id = actualAppOutputs[0]["image"]["domId"]
    url = urlunsplit(
        urlsplit(eyes.server_url)._replace(
            path="/api/images/dom/" + dom_id, query=urlencode({"apiKey": eyes.api_key})
        )
    )
    res = requests.get(url)
    return res.json()


@pytest.mark.skip
def test_send_dom_cors_iframe(dom_intercepting_eyes, driver, batch_info, expected_json):
    # Expected json data is captured by java sdk,
    # it produces arbitrary cd_frame_id_ attributes
    del expected_json["childNodes"][1]["childNodes"][13]["attributes"]["cd_frame_id_"]
    del expected_json["childNodes"][1]["childNodes"][13]["childNodes"][0]["childNodes"][
        1
    ]["childNodes"][3]["attributes"]["cd_frame_id_"]
    config = (
        Configuration()
        .set_batch(batch_info)
        .set_app_name("Test Send DOM")
        .set_test_name("test_send_dom_cors_iframe")
        .set_viewport_size(RectangleSize(1024, 768))
        # TODO: Remove this when default options get in sync for java and python SDK
        .set_hide_scrollbars(True)
    )
    dom_intercepting_eyes.set_configuration(config)

    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage")
    dom_intercepting_eyes.open(driver, "Test Send DOM", "test_send_dom_cors_iframe")
    dom_intercepting_eyes.check("Window", Target.window().fully())
    dom_intercepting_eyes.close(False)
    actual = json.loads(dom_intercepting_eyes.captured_dom_json)

    assert check_objects(actual, expected_json)

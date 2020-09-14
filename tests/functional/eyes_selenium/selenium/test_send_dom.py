import json
import os
from collections import OrderedDict

import pytest

from applitools.selenium import Configuration, Target
from applitools.selenium.capture import dom_capture
from tests.utils import get_session_results


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


@pytest.mark.skip
def test_send_DOM_full_window(eyes, driver, batch_info):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    config = Configuration().set_batch(batch_info)
    eyes.set_configuration(config)
    eyes_driver = eyes.open(
        driver,
        "Test Send DOM",
        "Full Window",
        viewport_size={"width": 1024, "height": 768},
    )
    eyes.check_window()
    actual_dom_json = dom_capture.get_full_window_dom(eyes_driver, return_as_dict=True)

    def get_expected_json(test_name):
        cur_dir = os.path.abspath(__file__).rpartition("/")[0]
        samples_dir = os.path.join(cur_dir, "resources")
        with open(os.path.join(samples_dir, test_name + ".json"), "r") as f:
            return json.loads(f.read(), object_pairs_hook=OrderedDict)

    expected_dom_json = get_expected_json("expected_dom1")
    results = eyes.close(False)
    assert get_has_DOM(eyes.api_key, results)
    assert actual_dom_json["attributes"] == expected_dom_json["attributes"]
    assert actual_dom_json["css"] == expected_dom_json["css"]
    assert actual_dom_json["images"] == expected_dom_json["images"]
    assert actual_dom_json["rect"] == expected_dom_json["rect"]
    assert actual_dom_json["scriptVersion"] == expected_dom_json["attributes"]
    assert actual_dom_json["style"] == expected_dom_json["style"]
    assert actual_dom_json["tagName"] == expected_dom_json["tagName"]
    assert actual_dom_json["version"] == expected_dom_json["version"]

    assert actual_dom_json == expected_dom_json


def get_has_DOM(api_key, results):
    session_results = get_session_results(api_key, results)
    actualAppOutputs = session_results["actualAppOutput"]
    assert len(actualAppOutputs) == 1
    return actualAppOutputs[0]["image"]["hasDom"]

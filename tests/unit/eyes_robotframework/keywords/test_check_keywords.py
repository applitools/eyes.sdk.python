from collections import namedtuple
from typing import List

import attr
import mock
import pytest
from mock import Mock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region
from applitools.core import RegionByRectangle
from applitools.selenium.fluent import FrameLocator, RegionBySelector
from EyesLibrary.keywords.check_settings import CheckSettingsKeywords

WEB_ELEMENT = Mock(WebElement)


def run_keyword(name, *args):
    if name == "Ignore Region By Coordinates":
        return CheckSettingsKeywords(Mock()).ignore_region_by_coordinates(*args)


CheckSettingsData = namedtuple("CheckSettingsData", "params result")


@attr.s
class TestData(object):
    method = attr.ib(type=str)
    check_tag = attr.ib(default=None)
    check_region = attr.ib(default=None)
    check_region_result = attr.ib(default=None)

    check_settings_data = CheckSettingsData(
        params=["Ignore Region By Coordinates", "[34 34 34 34]"],
        result=[RegionByRectangle(Region(34, 34, 34, 34))],
    )

    @property
    def check_params(self):
        # type: () -> List
        result = []
        # order does matter here!
        if self.check_region:
            result.append(self.check_region)
        if self.check_tag:
            result.append(self.check_tag)
        if self.check_settings_data.params:
            result.extend(self.check_settings_data.params)
        return result

    def __str__(self):
        return "{} {}".format(
            self.method, "with tag" if self.check_tag else "without tag"
        )


@pytest.mark.parametrize(
    "data",
    [
        TestData(
            "check_window",
        ),
        TestData("check_window", check_tag="Tag"),
    ],
    ids=lambda d: str(d),
)
def test_check_window(check_keyword, data):
    call_method = getattr(check_keyword, data.method)

    with mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.run_keyword", side_effect=run_keyword
    ):
        call_method(*data.check_params)

    check_settings, tag = check_keyword.results[0]
    assert tag == data.check_tag
    assert check_settings.values.ignore_regions == data.check_settings_data.result


@pytest.mark.parametrize(
    "data",
    [
        TestData(
            "check_region_by_coordinates",
            check_region="[20 20 20 20]",
            check_region_result=Region(20, 20, 20, 20),
        ),
        TestData(
            "check_region_by_selector",
            check_region="id:overflow-div",
            check_region_result=RegionBySelector(By.ID, "overflow-div"),
        ),
        TestData("check_region_by_element", check_region=WEB_ELEMENT),
    ],
    ids=lambda d: str(d),
)
def test_check_region(check_keyword, data):
    call_method = getattr(check_keyword, data.method)

    with mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.run_keyword", side_effect=run_keyword
    ):
        call_method(*data.check_params)

    check_settings, tag = check_keyword.results[0]
    assert tag == data.check_tag
    assert not check_settings.values.is_target_empty
    assert check_settings.values.ignore_regions == data.check_settings_data.result


@pytest.mark.parametrize(
    "data",
    [
        TestData(
            "check_frame_by_element",
            check_region=WEB_ELEMENT,
            check_region_result=FrameLocator(frame_element=WEB_ELEMENT),
        ),
        TestData(
            "check_frame_by_index",
            check_region=1,
            check_region_result=FrameLocator(frame_index=1),
        ),
        TestData(
            "check_frame_by_name",
            check_region="framename",
            check_region_result=FrameLocator(frame_name_or_id="framename"),
        ),
        TestData(
            "check_frame_by_selector",
            check_region="id:overflow-div",
            check_region_result=FrameLocator(frame_selector=[By.ID, "overflow-div"]),
        ),
    ],
    ids=lambda d: str(d),
)
def test_check_frame(check_keyword, data):
    call_method = getattr(check_keyword, data.method)

    with mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.run_keyword", side_effect=run_keyword
    ):
        call_method(*data.check_params)

    check_settings, tag = check_keyword.results[0]
    assert tag == data.check_tag
    assert check_settings.values.frame_chain == [data.check_region_result]
    assert check_settings.values.ignore_regions == data.check_settings_data.result

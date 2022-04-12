import sys

import pytest
import trafaret as t
import yaml

from applitools.selenium import BrowserType, RectangleSize, StitchMode
from EyesLibrary.config_parser import (
    ConfigurationTrafaret,
    TextToEnumTrafaret,
    UpperTextToEnumTrafaret,
    ViewPortTrafaret,
)


def test_text_to_enum_trafaret():
    assert BrowserType.CHROME == TextToEnumTrafaret(BrowserType).check("CHROME")
    assert StitchMode.CSS == TextToEnumTrafaret(StitchMode).check("CSS")

    with pytest.raises(t.DataError, match=r"Incorrect value `MissingBrowser`"):
        TextToEnumTrafaret(BrowserType).check("MissingBrowser")


def test_upper_text_to_enum_trafaret():
    assert BrowserType.CHROME == UpperTextToEnumTrafaret(BrowserType).check("CHROmE")
    assert StitchMode.CSS == UpperTextToEnumTrafaret(StitchMode).check("CSs")

    with pytest.raises(t.DataError, match=r"Incorrect value `MissingBrowser`"):
        UpperTextToEnumTrafaret(BrowserType).check("MissingBrowser")


def test_viewport_size_trafaret():
    expected_red = RectangleSize(400, 400)
    res = ViewPortTrafaret().check({"width": 400, "height": 400})
    assert res == expected_red
    res = ViewPortTrafaret().check("[400 400]")
    assert res == expected_red


EXAMPLE_CONFIG_YAML = """
### applitools.yaml 1.0
### START `SHARED SECTION` ###
server_url: "https://eyesapi.applitools.com" #optional
api_key: YOUR_API_KEY  #Could be specified as APPLITOOLS_API_KEY env variable

proxy:
  url: "http://someproxy-url.com"

properties:
  - name: YOUR_PROPERTY_NAME
    value: YOUR_PROPERTY_VALUE

###### START `AVAILABLE DURING `Eyes Open` CALL SECTION` ######
app_name: YOUR_APP_NAME
viewport_size:
  width: 1920
  height: 1080
branch_name: YOUR_BRANCH_NAME
parent_branch_name: YOUR_PARENT_BRANCH_NAME
baseline_branch_name: YOUR_BASELINE_BRANCH_NAME
baseline_env_name: YOUR_BASELINE_ENV_NAME
save_diffs: false
match_timeout: 600
save_new_tests: true  #optional
save_failed_tests: false  #optional

batch:  #optional
  id: YOUR_BATCH_ID  #optional
  name: YOUR_BATCH_NAME
  batch_sequence_name: YOUR_BATCH_SEQUENCE_NAME  #optional
  properties:    #optional
    - name: YOUR_BATCH_PROPERTY_NAME
      value: YOUR_BATCH_PROPERTY_VALUE

###### END `AVAILABLE DURING `Eyes Open` CALL SECTION` ######


### END `SHARED SECTION` ###

web:
  force_full_page_screenshot: false  #optional
  wait_before_screenshots: 100  #optional
  stitch_mode: CSS   # Scroll | CSS
  hide_scrollbars: true
  hide_caret: true
# ALL SETTINGS FROM `SHARED SECTION` COULD BE PASSED HERE AS WELL

mobile_native:
  is_simulator: false
# ALL SETTINGS FROM `SHARED SECTION` COULD BE PASSED HERE AS WELL


web_ufg:
  runner_options:
    test_concurrency: 5
  visual_grid_options:
    - key: YOUR_VISUAL_GRID_OPTION
      value: YOUR_VISUAL_GRID_OPTION_VALUE
  disable_browser_fetching: false
  enable_cross_origin_rendering: false
  dont_use_cookies: false
  layout_breakpoints: true
  browsers:
    desktop:
      - browser_type: CHROME  # names from BrowserType
        width: 800
        height: 600
    ios:
      - device_name: iPhone_12_Pro  # names from IosDeviceName
        screen_orientation: PORTRAIT  # PORTRAIT | LANDSCAPE
        ios_version: LATEST  # LATEST | ONE_VERSION_BACK
    chrome_emulation:
      - device_name: iPhone_4  # names from DeviceName
        screen_orientation: PORTRAIT  # PORTRAIT | LANDSCAPE
"""


@pytest.mark.parametrize("config", [EXAMPLE_CONFIG_YAML])
def test_all_values_in_example_config(config):
    ConfigurationTrafaret.scheme.check(yaml.safe_load(config))

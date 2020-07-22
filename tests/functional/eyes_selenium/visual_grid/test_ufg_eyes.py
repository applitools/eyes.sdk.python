import json
import re
from mock import patch

from applitools.selenium import Eyes, eyes_selenium_utils


def _fetch_skip_resources(resource_script_string):
    skip_list_pattern = re.compile(r"\"skipResources\": (\[[\w\W]+\])")
    skip_resources = json.loads(
        re.search(skip_list_pattern, resource_script_string).group(1)
    )
    return skip_resources


def test_ufg_skip_list(vg_runner, driver):
    # TODO: Refactor this to unit test
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.com/")
    eyes.open(driver, test_name="TestUFGSkipList")
    eyes.check_window()
    eyes.check_window()
    with patch(
        "applitools.selenium.eyes_selenium_utils.get_dom_script_result",
        wraps=eyes_selenium_utils.get_dom_script_result,
    ) as get_script_result:
        eyes.check_window()
        resources = _fetch_skip_resources(get_script_result.call_args[0][3])
    eyes.close_async()
    vg_runner.get_all_test_results(False)
    print(resources)
    assert resources

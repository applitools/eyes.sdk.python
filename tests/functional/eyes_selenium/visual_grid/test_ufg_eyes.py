import json
import re
from mock import patch

from applitools.selenium import Eyes, eyes_selenium_utils


def _fetch_skip_resources(resource_script_string):
    skip_list_pattern = re.compile(r"\"skipResources\": (\[[\w\W]+\])")
    skip_resources = re.search(skip_list_pattern, resource_script_string)
    if not skip_resources:
        return None
    return json.loads(skip_resources.group(1))


def _retrieve_urls(data):
    return dict(
        blobs=[b["url"] for b in data.get("blobs", [])],
        resource_urls=data.get("resourceUrls", []),
    )


def test_ufg_skip_list(vg_runner, driver):
    # TODO: Refactor this to unit test
    eyes = Eyes(vg_runner)
    driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPageWithRelativeBGImage/index.html"
    )
    eyes.open(driver, app_name="TestUFGEyes", test_name="TestUFGSkipList")

    running_test = vg_runner._get_all_running_tests()[0]

    eyes.check_window("check 1")
    eyes.check_window("check 2")

    with patch(
        "applitools.selenium.eyes_selenium_utils.get_dom_script_result",
        wraps=eyes_selenium_utils.get_dom_script_result,
    ) as get_script_result:
        with patch(
            "applitools.selenium.visual_grid.running_test.RunningTest.check",
            wraps=running_test.check,
        ) as running_check:
            eyes.check_window("check 3")

            skip_list = _fetch_skip_resources(get_script_result.call_args[0][3])
            script_result = _retrieve_urls(running_check.call_args[1]["script_result"])
            assert set(skip_list).difference(script_result["resource_urls"])

    eyes.close_async()
    vg_runner.get_all_test_results(False)

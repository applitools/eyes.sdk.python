import typing
from json import dumps, loads

from applitools.common import MatchResult, TestResults
from applitools.common.utils.json_utils import attr_from_json, to_json

if typing.TYPE_CHECKING:
    from typing import List

    from selenium.webdriver.remote.webdriver import WebDriver

    from applitools.common import Configuration

    from .fluent import SeleniumCheckSettings


def marshal_webdriver_ref(driver):
    # type: (WebDriver) -> dict
    return {
        "serverUrl": driver.command_executor._url,  # noqa
        "sessionId": driver.session_id,
        "capabilities": driver.capabilities,
    }


def marshal_configuration(configuration):
    # type: (Configuration) -> dict
    return loads(to_json(configuration))


def marshal_check_settings(check_settings):
    # type: (SeleniumCheckSettings) -> dict
    return loads(to_json(check_settings.values))


def demarshal_match_result(results_dict):
    # type: (dict) -> MatchResult
    return attr_from_json(dumps(results_dict), MatchResult)


def demarshal_test_results(results_dict_list):
    # type: (List[dict]) -> List[TestResults]
    return [attr_from_json(dumps(r), TestResults) for r in results_dict_list]

import json

import pytest

from applitools.common import (
    RenderRequest,
    RGridDom,
    VGResource,
    RenderInfo,
    RunningSession,
    TestResults,
    RectangleSize,
    Region,
)
from applitools.common.accessibility import (
    SessionAccessibilityStatus,
    AccessibilityStatus,
    AccessibilityLevel,
    AccessibilityGuidelinesVersion,
    AccessibilityRegionType,
)
from applitools.common.geometry import AccessibilityRegion
from applitools.common.selenium import BrowserType
from applitools.common.test_results import TestResultsStatus
from applitools.common.utils import json_utils
from tests.utils import get_resource


@pytest.mark.parametrize(
    "browser_type",
    [
        BrowserType.CHROME,
        BrowserType.CHROME_ONE_VERSION_BACK,
        BrowserType.CHROME_TWO_VERSIONS_BACK,
        BrowserType.FIREFOX,
        BrowserType.FIREFOX_ONE_VERSION_BACK,
        BrowserType.FIREFOX_TWO_VERSIONS_BACK,
        BrowserType.SAFARI_ONE_VERSION_BACK,
        BrowserType.SAFARI_TWO_VERSIONS_BACK,
    ],
)
def test_render_request_serialize(browser_type):

    request_resources = {"url": VGResource.EMPTY("some-url.com")}
    dom_url = "dom-url.com"
    r_info = RenderInfo(
        width=500,
        height=600,
        size_mode="full-page",
        selector=None,
        region=None,
        emulation_info=None,
    )
    dom = RGridDom(url=dom_url, dom_nodes=[{}], resources=request_resources)
    requests = [
        RenderRequest(
            webhook="some-webhook.com",
            agent_id="my-agent-id",
            stitching_service="https://some.stitchingserviceuri.com",
            url=dom_url,
            dom=dom,
            resources=request_resources,
            render_info=r_info,
            browser_name=browser_type.value,
            platform_name="linux",
            script_hooks=dict(),
            selectors_to_find_regions_for=[],
            send_dom=False,
        )
    ]
    test_results_data = get_resource("unit/renderResult.json").decode("utf-8")
    test_results_data %= browser_type.value
    assert json.loads(test_results_data) == json.loads(json_utils.to_json(requests))


def test_running_session_serialization_and_deserialization():
    rs = RunningSession(
        id="some-id",
        session_id="session-id",
        batch_id="batch-id",
        baseline_id="baseline_id",
        url="url",
        is_new_session=True,
    )
    rs_json = json_utils.to_json(rs)
    assert '"isNew": true' in rs_json
    assert rs == json_utils.attr_from_json(rs_json, RunningSession)


def test_test_results_deserialization():
    tr = json_utils.attr_from_json(
        get_resource("unit/testResultsData.json"), TestResults
    )  # type: TestResults
    assert tr.status == TestResultsStatus.Passed
    assert (
        tr.app_urls.batch
        == "https://eyes.applitools.com/app/test-results/111?accountIdPczBANNug~~"
    )
    assert tr.accessibility_status == SessionAccessibilityStatus(
        AccessibilityStatus.Failed,
        AccessibilityLevel.AA,
        AccessibilityGuidelinesVersion.WCAG_2_0,
    )
    assert tr.host_display_size == RectangleSize(800, 800)
    assert tr.default_match_settings.ignore_regions == [Region(300, 300, 300, 300)]
    assert tr.default_match_settings.accessibility == [
        AccessibilityRegion(300, 300, 300, 300, AccessibilityRegionType.BoldText)
    ]
    assert tr.steps_info[0].name == "Login Window"
    assert (
        tr.steps_info[0].app_urls.step
        == "https://eyes.applitools.com/app/test-results/00000215/steps/1?accountId=~"
    )

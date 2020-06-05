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
    dom = RGridDom(url=dom_url, dom_nodes=[{}], resources=request_resources,)
    requests = [
        RenderRequest(
            webhook="some-webhook.com",
            agent_id="my-agent-id",
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
    RESULT_PATTERN = '[{"agentId": "my-agent-id", "browser": {"name": "%s"}, "platform": {"name": "linux"}, "dom": {"hash": "a67486a8bc9ba45f878e5b0d8ff9bc68ec6ed9db0382709751327d1793898e16", "hashFormat": "sha256"}, "renderId": null, "renderInfo": {"height": 600, "sizeMode": "full-page", "width": 500}, "resources": {"url": {"contentType": "application/empty-response", "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "hashFormat": "sha256"}}, "scriptHooks": {}, "selectorsToFindRegionsFor": [], "sendDom": false, "url": "dom-url.com", "webhook": "some-webhook.com"}]'
    RESULT_PATTERN %= browser_type.value
    assert json.loads(RESULT_PATTERN) == json.loads(json_utils.to_json(requests))


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


TEST_RESULTS_DATA = """
{
	"exactMatches": 0,
	"strictMatches": 0,
	"contentMatches": 0,
	"layoutMatches": 0,
	"noneMatches": 0,
	"steps": 2,
	"matches": 2,
	"mismatches": 0,
	"missing": 0,
	"new": 0,
	"name": "Classic Runner",
	"secretToken": "Secrettoken",
	"id": "00000",
	"status": "Passed",
	"accessibilityStatus": {
		"status": "Failed",
		"level": "AA",
		"version": "WCAG_2_0"
	},
	"appName": "Demo App",
	"baselineId": "k~!~!4179-edc9c988",
	"batchName": "Classic Runner",
	"batchId": "000002519",
	"branchName": "default",
	"hostOS": "Linux",
	"hostApp": "Chrome",
	"hostDisplaySize": {
		"width": 800,
		"height": 800
	},
	"startedAt": "2020-05-14T10:48:49.9189634+00:00",
	"duration": 38,
	"isNew": false,
	"isDifferent": false,
	"isAborted": false,
	"defaultMatchSettings": {
		"matchLevel": "Strict",
		"ignore": [{"left": 300, "top": 300, "width": 300, "height": 300}],
		"strict": [],
		"content": [],
		"layout": [],
		"floating": [],
		"accessibility": [{"left": 300, "top": 300, "width": 300, "height": 300, "type": "BoldText"}],
		"splitTopHeight": 0,
		"splitBottomHeight": 0,
		"ignoreCaret": true,
		"accessibilitySettings": {
			"level": "AA",
			"version": "WCAG_2_0"
		},
		"ignoreDisplacements": false,
		"scale": 1.0,
		"remainder": 0.0,
		"useDom": false,
		"useDL": false,
		"enablePatterns": false
	},
	"appUrls": {
		"batch": "https://eyes.applitools.com/app/test-results/111?accountIdPczBANNug~~",
		"session": "https://eyes.applitools.com/app/test-results//00000?account"
	},
	"apiUrls": {
		"batch": "https://eyesapi.applitools.com/api/sessions/batches/0000025",
		"session": "https://eyesapi.applitools.com/api/sessions/batches/0000025/000002518"
	},
	"stepsInfo": [{
		"name": "Login Window",
		"isDifferent": false,
		"hasBaselineImage": true,
		"hasCurrentImage": true,
		"hasCheckpointImage": true,
		"appUrls": {
			"step": "https://eyes.applitools.com/app/test-results/00000215/steps/1?accountId=~",
			"stepEditor": "https://eyes.applitools.com/app/test-results/8/steps/1/edit?accountId="
		},
		"apiUrls": {
			"baselineImage": "https://eyesapi.applitools.com/api/images/se~cff89",
			"currentImage": "https://eyesapi.applitools.com/api/sessions/batches/00000/00000/steps/1/images/checkpoint",
			"checkpointImage": "https://eyesapi.applitools.com/api/sessions/batches/00000/00000/steps/1/images/checkpoint",
			"checkpointImageThumbnail": "https://eyesapi.applitools.com/api/sessions/batches/00000/00000/steps/1/images/checkpoint-thumbnail",
			"diffImage": "https://eyesapi.applitools.com/api/sessions/batches/00000/00000/steps/1/images/diff"
		}
	}]
}"""


def test_test_results_deserialization():
    tr = json_utils.attr_from_json(TEST_RESULTS_DATA, TestResults)  # type: TestResults
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

import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from applitools.common import (
    AppOutput,
    ImageMatchSettings,
    MatchWindowData,
    Options,
    RectangleSize,
    Region,
    RunningSession,
    TestResults,
)
from applitools.common.accessibility import (
    AccessibilityGuidelinesVersion,
    AccessibilityLevel,
    AccessibilityRegionType,
    AccessibilityStatus,
    SessionAccessibilityStatus,
)
from applitools.common.geometry import AccessibilityRegion
from applitools.common.selenium import BrowserType
from applitools.common.test_results import TestResultsStatus
from applitools.common.utils import json_utils
from tests.utils import get_resource


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


@pytest.mark.parametrize("i", range(5))
def test_multithreading_serialization(i):
    mwd = MatchWindowData(
        agent_setup=None,
        app_output=AppOutput(
            dom_url="https://eyespublicwusi0.core/bl9crP4n81pwT9anq3r1Xr8g0e97eMliN8f7etrM110",
            screenshot_url="https://eyespublicwusi0.blob.core/g0e97eMliN8f7etrM110",
            viewport=RectangleSize(height=1300, width=2560),
            title="",
            screenshot_bytes=None,
        ),
        ignore_mismatch=False,
        user_inputs=[],
        tag="Capture",
        render_id="bf3ce18291b4aa933bee",
        options=Options(
            force_match=False,
            force_mismatch=False,
            ignore_mismatch=False,
            ignore_match=False,
            image_match_settings=ImageMatchSettings(
                ignore_regions=[
                    Region(height=41, left=30, top=165, width=738),
                    Region(height=32, left=30, top=480, width=738),
                ]
            ),
            name="Capture",
            render_id="bf3ce18291b4aa933bee",
            replace_last=False,
            source="applitoolscasppe.cm",
            user_inputs=[],
            variant_id="Some-id",
        ),
    )
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(json_utils.to_json, [mwd] * 100))

    assert len(results) == 100

    for i, r in enumerate(results):
        assert "Ignore" in r
        assert "ignoreRegions" not in r


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

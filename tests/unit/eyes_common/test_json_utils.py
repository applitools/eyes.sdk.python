from concurrent.futures import ThreadPoolExecutor

import pytest

from applitools.common import (
    AppOutput,
    ImageMatchSettings,
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

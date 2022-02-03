from __future__ import absolute_import

from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Text, Tuple

import attr

from applitools.common.utils.json_utils import JsonInclude

from .accessibility import SessionAccessibilityStatus
from .geometry import RectangleSize
from .match import ImageMatchSettings

if TYPE_CHECKING:
    from . import ProxySettings
    from .ultrafastgrid import RenderBrowserInfo


__all__ = ("TestResults", "TestResultsSummary", "TestResultContainer")


class TestResultsStatus(Enum):
    """
    Status values for tests results.
    """

    Passed = "Passed"
    Unresolved = "Unresolved"
    Failed = "Failed"

    __test__ = False  # avoid warnings in test frameworks


@attr.s
class SessionUrls(object):
    batch = attr.ib(default=None, metadata={JsonInclude.THIS: True})  # type: Text
    session = attr.ib(default=None, metadata={JsonInclude.THIS: True})  # type: Text


@attr.s
class StepInfo(object):
    @attr.s(repr_ns="StepInfo")
    class AppUrls(object):
        step = attr.ib(default=None, metadata={JsonInclude.THIS: True})  # type: Text
        step_editor = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text

    @attr.s(repr_ns="StepInfo")
    class ApiUrls(object):
        baseline_image = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text
        current_image = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text
        diff_image = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text
        checkpoint_image = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text
        checkpoint_image_thumbnail = attr.ib(
            default=None, metadata={JsonInclude.THIS: True}
        )  # type: Text

    name = attr.ib(default=None, metadata={JsonInclude.THIS: True})  # type: Text
    is_different = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: bool
    has_baseline_image = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: bool
    has_current_image = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: bool
    has_checkpoint_image = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: bool
    api_urls = attr.ib(
        default=None, type=ApiUrls, metadata={JsonInclude.THIS: True}
    )  # type: ApiUrls
    app_urls = attr.ib(
        default=None, type=AppUrls, metadata={JsonInclude.THIS: True}
    )  # type: AppUrls


@attr.s
class TestResults(object):
    """
    Eyes test results.
    """

    steps = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    matches = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    mismatches = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    missing = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    exact_matches = attr.ib(
        default=0, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    strict_matches = attr.ib(
        default=0, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    content_matches = attr.ib(
        default=0, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    layout_matches = attr.ib(
        default=0, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    none_matches = attr.ib(
        default=0, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    is_new = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]

    url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    status = attr.ib(
        converter=lambda v: TestResultsStatus(v) if v else None,
        type=TestResultsStatus,
        default=None,
        repr=False,
        metadata={JsonInclude.THIS: True},
    )  # type: Optional[TestResultsStatus]

    name = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    secret_token = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    id = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    app_name = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    batch_name = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    batch_id = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    branch_name = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    host_os = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    host_app = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    host_display_size = attr.ib(
        default=None, repr=False, type=RectangleSize, metadata={JsonInclude.THIS: True}
    )  # type: RectangleSize
    started_at = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    duration = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    is_different = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: bool
    is_aborted = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: bool
    is_empty = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: bool
    app_urls = attr.ib(
        default=None, repr=False, type=SessionUrls, metadata={JsonInclude.THIS: True}
    )  # type: SessionUrls
    api_urls = attr.ib(
        default=None, repr=False, type=SessionUrls, metadata={JsonInclude.THIS: True}
    )  # type: SessionUrls
    steps_info = attr.ib(
        default=None, repr=False, type=StepInfo, metadata={JsonInclude.THIS: True}
    )  # type: List[StepInfo]
    baseline_id = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Text
    default_match_settings = attr.ib(
        default=None,
        repr=False,
        type=ImageMatchSettings,
        metadata={JsonInclude.THIS: True},
    )  # type: ImageMatchSettings
    accessibility_status = attr.ib(
        default=None,
        type=SessionAccessibilityStatus,
        metadata={JsonInclude.THIS: True},
    )  # type: SessionAccessibilityStatus
    _connection_config = attr.ib(
        default=(None, None, None),
        eq=False,
        order=False,
        metadata={JsonInclude.THIS: False},
        repr=False,
    )  # type: Tuple[Optional[Text], Optional[Text], Optional[ProxySettings]]
    __test__ = False  # avoid warnings in test frameworks

    @property
    def is_passed(self):
        # type: () -> bool
        return self.status == TestResultsStatus.Passed

    @property
    def is_unresolved(self):
        # type: () -> bool
        return self.status == TestResultsStatus.Unresolved

    @property
    def is_failed(self):
        # type: () -> bool
        return self.status == TestResultsStatus.Failed

    def set_connection_config(self, server_url, api_key, proxy_settings):
        # type: (Text, Text, Optional[ProxySettings]) -> None
        self._connection_config = (server_url, api_key, proxy_settings)

    def delete(self):
        # type: () -> None
        from applitools.selenium.__version__ import __version__
        from applitools.selenium.command_executor import CommandExecutor
        from applitools.selenium.eyes import EyesRunner
        from applitools.selenium.universal_sdk_types import marshal_delete_test_settings

        cmd = CommandExecutor.get_instance(EyesRunner.BASE_AGENT_ID, __version__)
        marshaled = marshal_delete_test_settings(self)
        cmd.core_delete_test(marshaled)


@attr.s(repr=False, str=False)
class TestResultContainer(object):
    test_results = attr.ib()  # type: TestResults
    browser_info = attr.ib()  # type: Optional[RenderBrowserInfo]
    exception = attr.ib()  # type: Optional[Exception]

    def __str__(self):
        browser_info = (
            "\n browser_info = {}".format(self.browser_info)
            if self.browser_info
            else ""
        )
        return (
            "TestResultContainer{{"
            "\n test_results = {test_results}"
            "{browser_info}"
            "\n exception = {exception}"
            "}}".format(
                test_results=self.test_results,
                browser_info=browser_info,
                exception=self.exception,
            )
        )


@attr.s(repr=False, str=False)
class TestResultsSummary(object):
    _all_results = attr.ib()  # type: List[TestResultContainer]
    _exceptions = attr.ib(init=False, default=0)  # type: int
    _passed = attr.ib(init=False, default=0)  # type: int
    _unresolved = attr.ib(init=False, default=0)  # type: int
    _failed = attr.ib(init=False, default=0)  # type: int
    _mismatches = attr.ib(init=False, default=0)  # type: int
    _missing = attr.ib(init=False, default=0)  # type: int
    _matches = attr.ib(init=False, default=0)  # type: int

    @property
    def all_results(self):
        # type: () -> List[TestResultContainer]
        return self._all_results

    def size(self):
        # type: () -> int
        return len(self)

    def __attrs_post_init__(self):
        for result_container in self._all_results:
            if result_container and result_container.exception:
                self._exceptions += 1

            result = result_container.test_results
            if result is None:
                continue
            if result.is_failed:
                self._failed += 1
            elif result.is_passed:
                self._passed += 1
            elif result.is_unresolved:
                self._unresolved += 1
            self._matches += result.matches
            self._missing += result.missing
            self._mismatches += result.mismatches

    def __len__(self):
        return len(self._all_results)

    def __iter__(self):
        return iter(self._all_results)

    def __getitem__(self, item):
        # type: (int) -> TestResultContainer
        return self._all_results[item]

    def __str__(self):
        return """
result summary {{
    all results={all_results}
    passed={passed}
    unresolved={unresolved}
    failed={failed}
    exceptions={exceptions}
    mismatches={mismatches}
    missing={missing}
    matches={matches}
}}""".format(
            all_results="\n".join(map(str, self._all_results)),
            passed=self._passed,
            unresolved=self._unresolved,
            failed=self._failed,
            exceptions=self._exceptions,
            mismatches=self._mismatches,
            missing=self._missing,
            matches=self._matches,
        )

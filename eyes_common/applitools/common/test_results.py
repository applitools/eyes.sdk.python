from __future__ import absolute_import

import typing
from enum import Enum

import attr

from .geometry import RectangleSize
from .match import ImageMatchSettings

if typing.TYPE_CHECKING:
    from typing import Text, Optional, List
    from .utils.custom_types import SessionUrls, StepInfo
    from .visual_grid import RenderBrowserInfo


__all__ = ("TestResults", "TestResultsSummary", "TestResultContainer")


class TestResultsStatus(Enum):
    """
    Status values for tests results.
    """

    Passed = "Passed"
    Unresolved = "Unresolved"
    Failed = "Failed"


@attr.s
class TestResults(object):
    """
    Eyes test results.
    """

    steps = attr.ib(default=0)  # type: int
    matches = attr.ib(default=0)  # type: int
    mismatches = attr.ib(default=0)  # type: int
    missing = attr.ib(default=0)  # type: int
    exact_matches = attr.ib(default=0, repr=False)  # type: int
    strict_matches = attr.ib(default=0, repr=False)  # type: int
    content_matches = attr.ib(default=0, repr=False)  # type: int
    layout_matches = attr.ib(default=0, repr=False)  # type: int
    none_matches = attr.ib(default=0, repr=False)  # type: int
    is_new = attr.ib(default=None, repr=False)  # type: Optional[bool]

    url = attr.ib(init=False, default=None)  # type: Optional[Text]
    status = attr.ib(default=None, repr=False)  # type: Optional[Text]

    name = attr.ib(default=None, repr=False)  # type: Text
    secret_token = attr.ib(default=None, repr=False)  # type: Text
    id = attr.ib(default=None, repr=False)  # type: Text
    app_name = attr.ib(default=None, repr=False)  # type: Text
    batch_name = attr.ib(default=None, repr=False)  # type: Text
    batch_id = attr.ib(default=None, repr=False)  # type: Text
    branch_name = attr.ib(default=None, repr=False)  # type: Text
    host_os = attr.ib(default=None, repr=False)  # type: Text
    host_app = attr.ib(default=None, repr=False)  # type: Text
    host_display_size = attr.ib(default=None, repr=False)  # type: RectangleSize
    # started_at = attr.ib(
    #     default=None,
    #     repr=False,
    #     converter=lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ"),
    # )  # type: datetime
    started_at = attr.ib(default=None, repr=False)  # type: Text
    duration = attr.ib(default=None, repr=False)  # type: int
    is_different = attr.ib(default=None, repr=False)  # type: bool
    is_aborted = attr.ib(default=None, repr=False)  # type: bool
    app_urls = attr.ib(default=None, repr=False)  # type: SessionUrls
    api_urls = attr.ib(default=None, repr=False)  # type: SessionUrls
    steps_info = attr.ib(default=None, repr=False)  # type: StepInfo
    baseline_id = attr.ib(default=None, repr=False)  # type: Text
    default_match_settings = attr.ib(
        default=None, repr=False, type=ImageMatchSettings
    )  # type: ImageMatchSettings

    @property
    def is_passed(self):
        # type: () -> bool
        return (
            self.status is not None
        ) and self.status.lower() == TestResultsStatus.Passed.name.lower()

    @property
    def is_unresolved(self):
        # type: () -> bool
        return (
            self.status is not None
        ) and self.status.lower() == TestResultsStatus.Unresolved.name.lower()

    @property
    def is_failed(self):
        # type: () -> bool
        return (
            self.status is not None
        ) and self.status.lower() == TestResultsStatus.Failed.name.lower()

    def __str__(self):
        origin_str = super(TestResults, self).__str__()
        preamble = "New test" if self.is_new else "Existing test"
        return "{} [{}]".format(preamble, origin_str)


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
            all_results=self._all_results,
            passed=self._passed,
            unresolved=self._unresolved,
            failed=self._failed,
            exceptions=self._exceptions,
            mismatches=self._mismatches,
            missing=self._missing,
            matches=self._matches,
        )

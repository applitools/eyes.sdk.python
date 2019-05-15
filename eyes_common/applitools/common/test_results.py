from __future__ import absolute_import

import typing
from enum import Enum

import attr

from .geometry import RectangleSize
from .match import ImageMatchSettings

if typing.TYPE_CHECKING:
    from typing import Text, Any, Dict, Optional, List

    # TODO: Implement objects
    SessionUrls = Dict[Any, Any]
    StepInfo = Dict[Any, Any]

__all__ = ("TestResults", "TestResultSummary")


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
    default_match_settings = attr.ib(default=None, repr=False, type=ImageMatchSettings)

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


@attr.s
class TestResultSummary(object):
    all_results = attr.ib()  # type: List[TestResults]
    exceptions = attr.ib(default=0)

    passed = attr.ib(init=False, default=0)
    unresolved = attr.ib(init=False, default=0)
    failed = attr.ib(init=False, default=0)
    mismatches = attr.ib(init=False, default=0)
    missing = attr.ib(init=False, default=0)
    matches = attr.ib(init=False, default=0)

    def __attrs_post_init__(self):
        for result in self.all_results:
            if result is None:
                continue
            if result.is_failed:
                self.failed += 1
            elif result.is_passed:
                self.passed += 1
            elif result.is_unresolved:
                self.unresolved += 1
            self.matches += result.matches
            self.missing += result.missing
            self.mismatches += result.mismatches

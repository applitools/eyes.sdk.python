from __future__ import absolute_import

import typing as tp

__all__ = ("TestResults", "TestResultsStatus")


class TestResultsStatus(object):
    """
    Status values for tests results.
    """

    Passed = "Passed"
    Unresolved = "Unresolved"
    Failed = "Failed"

    @classmethod
    def get_status(cls, status):
        # type: (tp.Optional[tp.Text]) -> tp.Text
        status = status.lower() if status is not None else ""
        if status == cls.Passed.lower():
            return cls.Passed
        elif status == cls.Unresolved.lower():
            return cls.Unresolved
        elif status == cls.Failed.lower():
            return cls.Failed
        else:
            # Unknown status
            return status


class TestResults(object):
    """
    Eyes test results.

    # TODO: update regarding JAVA SDK
    """

    def __init__(
        self,
        steps=0,  # type: int
        matches=0,  # type: int
        mismatches=0,  # type: int
        missing=0,  # type: int
        exact_matches=0,  # type: int
        strict_matches=0,  # type: int
        content_matches=0,  # type: int
        layout_matches=0,  # type: int
        none_matches=0,  # type: int
        status=None,  # type: tp.Optional[tp.Text]
    ):
        # type: (...) -> None
        self.steps = steps
        self.matches = matches
        self.mismatches = mismatches
        self.missing = missing
        self.exact_matches = exact_matches
        self.strict_matches = strict_matches
        self.content_matches = content_matches
        self.layout_matches = layout_matches
        self.none_matches = none_matches
        self._status = status
        self.is_new = None  # type: tp.Optional[bool]
        self.url = None  # type: tp.Optional[tp.Text]

    @property
    def status(self):
        # type: () -> tp.Text
        return TestResultsStatus.get_status(self._status)

    @status.setter
    def status(self, value):
        # type: (tp.Text) -> None
        self._status = value

    @property
    def is_passed(self):
        # type: () -> bool
        return (
            self.status is not None
        ) and self.status.lower() == TestResultsStatus.Passed.lower()

    def _to_dict(self):
        return dict(
            steps=self.steps,
            matches=self.matches,
            mismatches=self.mismatches,
            missing=self.missing,
            exact_matches=self.exact_matches,
            strict_matches=self.strict_matches,
            content_matches=self.content_matches,
            layout_matches=self.layout_matches,
            none_matches=self.none_matches,
            is_new=self.is_new,
            url=self.url,
            status=self.status,
        )

    def __str__(self):
        if self.is_new is not None:
            is_new = "New test" if self.is_new else "Existing test"
        else:
            is_new = ""
        return "%s [ steps: %d, matches: %d, mismatches: %d, missing: %d ], URL: %s" % (
            is_new,
            self.steps,
            self.matches,
            self.mismatches,
            self.missing,
            self.url,
        )

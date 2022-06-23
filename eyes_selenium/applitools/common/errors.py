__all__ = (
    "DiffsFoundError",
    "EyesError",
    "NewTestError",
    "OutOfBoundsError",
    "TestFailedError",
    "USDKFailure",
)


class EyesError(Exception):
    """
    Applitools Eyes Exception.
    """


class OutOfBoundsError(EyesError):
    """
    Indicates that an element is outside a specific boundary (e.g, region outside a frame,
    or point outside an image).
    """


class EyesServiceUnavailableError(EyesError):
    """Indicates that Eyes concurrency limit is exceeded"""


class TestFailedError(Exception):
    """
    Indicates that a test did not pass (i.e., test either failed or is a new test).
    """

    __test__ = False  # avoid warnings in test frameworks

    def __init__(
        self, test_results=None, scenario_id_or_name=None, app_id_or_name=None
    ):
        if all([test_results, scenario_id_or_name, app_id_or_name]):
            msg = "'{}' of '{}'. See details at {}".format(
                scenario_id_or_name, app_id_or_name, test_results.url
            )
            self._test_results = test_results
        else:
            msg = test_results
        super(TestFailedError, self).__init__(msg)


class NewTestError(TestFailedError):
    """
    Indicates that a test is a new test.
    """


class DiffsFoundError(TestFailedError):
    """
    Indicates that an existing test ended, and that differences where found from the baseline.
    """


class USDKFailure(EyesError):
    """
    Generic error raised by Universal SDK
    """

    def __init__(self, message, usdk_stack):
        super(USDKFailure, self).__init__(message)
        self.usdk_stack = usdk_stack

    def __str__(self):
        return super(USDKFailure, self).__str__() + "\n" + self.usdk_stack
